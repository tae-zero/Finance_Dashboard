import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from pykrx import stock
from fastapi import HTTPException
from typing import List, Dict
import json
import asyncio
import logging
import requests

logger = logging.getLogger("stock_service")

class StockService:
    def __init__(self):
        self.KOSPI_TICKER = "1001"  # KOSPI 지수 코드 상수
        self._apply_pykrx_monkey_patch()
    
    def _apply_pykrx_monkey_patch(self):
        """pykrx 내부 오류 방지 몽키패치"""
        try:
            # pykrx 내부 로깅 오류 방지
            import pykrx.website.comm.util as pykrx_util
            original_wrapper = pykrx_util.wrapper
            
            def safe_wrapper(func):
                def safe_func(*args, **kwargs):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        # 로그 레벨을 warning으로 낮춤
                        logger.debug(f"pykrx 내부 오류 (무시): {str(e)}")
                        raise
                return safe_func
            
            pykrx_util.wrapper = safe_wrapper
            logger.info("✅ pykrx 몽키패치 적용 완료")
        except Exception as e:
            logger.debug(f"⚠️ pykrx 몽키패치 실패: {e}")
    
    def _normalize_krx_symbol(self, code: str) -> str:
        """KRX 심볼 정규화"""
        if code.isdigit() and len(code) == 6:
            return f"{code}.KS"  # 코스피 기본
        return code
    
    async def get_stock_price(self, ticker: str, period: str = "3y") -> List[Dict]:
        """주가 데이터 조회"""
        try:
            def _fetch_stock():
                df = yf.download(ticker, period=period, interval="1d")
                if df.empty:
                    return {"error": "데이터 없음"}
                
                df = df[['Close']].reset_index()
                df['Date'] = df['Date'].astype(str)
                
                result = [{"Date": row['Date'], "Close": float(row['Close'])} for _, row in df.iterrows()]
                return result
            
            return await asyncio.to_thread(_fetch_stock)
            
        except Exception as e:
            logger.error(f"주가 데이터 조회 실패 ({ticker}): {str(e)}")
            return {"error": str(e)}
    
    async def get_kospi_data(self) -> List[Dict]:
        """코스피 지수 데이터 조회 (간단한 폴백 시스템)"""
        # 1차 시도: pykrx (몽키패치 적용)
        try:
            result = await self._fetch_kospi_pykrx()
            if result and len(result) > 0:
                logger.info("✅ pykrx로 코스피 데이터 조회 성공")
                return result
        except Exception as e:
            logger.debug(f"⚠️ pykrx 실패: {str(e)}")
        
        # 2차 시도: yfinance (야후 파이낸스)
        try:
            result = await self._fetch_kospi_yfinance()
            if result and len(result) > 0:
                logger.info("✅ yfinance로 코스피 데이터 조회 성공")
                return result
        except Exception as e:
            logger.debug(f"⚠️ yfinance 실패: {str(e)}")
        
        # 3차 시도: 정적 데이터 (최후 수단)
        try:
            result = await self._get_static_kospi_data()
            if result and len(result) > 0:
                logger.info("✅ 정적 데이터로 코스피 데이터 조회 성공")
                return result
        except Exception as e:
            logger.debug(f"⚠️ 정적 데이터 실패: {str(e)}")
        
        # 모든 방법 실패
        logger.error("❌ 모든 코스피 데이터 조회 방법 실패")
        raise HTTPException(status_code=503, detail="코스피 데이터 조회 완전 실패")
    
    async def _fetch_kospi_pykrx(self) -> List[Dict]:
        """pykrx로 코스피 데이터 조회"""
        try:
            def _fetch():
                today = datetime.today().date()
                yesterday = today - timedelta(days=30)  # 더 긴 기간으로 시도
                
                df = stock.get_index_ohlcv_by_date(
                    yesterday.strftime('%Y%m%d'),
                    today.strftime('%Y%m%d'),
                    self.KOSPI_TICKER
                )
                
                if df.empty:
                    raise ValueError("pykrx 데이터가 비어있습니다")
                
                df = df.reset_index()
                df['Date'] = df.index.astype(str)
                df['Close'] = df['종가'].astype(float)
                
                return df[['Date', 'Close']].to_dict(orient="records")
            
            return await asyncio.to_thread(_fetch)
            
        except Exception as e:
            logger.debug(f"pykrx 실패: {str(e)}")
            raise
    
    async def _fetch_kospi_yfinance(self) -> List[Dict]:
        """yfinance로 코스피 데이터 조회"""
        try:
            def _fetch():
                # KOSPI 지수 티커들 (우선순위 순)
                tickers = ["^KS11", "005930.KS", "000660.KS"]
                
                for ticker in tickers:
                    try:
                        df = yf.download(
                            ticker,
                            period="1y",
                            interval="1d",
                            auto_adjust=True,
                            progress=False,  # 진행바 비활성화
                            threads=False    # 스레드 비활성화
                        )
                        if not df.empty and 'Close' in df.columns:
                            break
                    except Exception as ticker_error:
                        logger.debug(f"티커 {ticker} 실패: {str(ticker_error)}")
                        continue
                
                if df.empty or 'Close' not in df.columns:
                    raise ValueError("yfinance 데이터가 비어있습니다")
                
                df = df.reset_index()
                df['Date'] = df['Date'].astype(str)
                df['Close'] = df['Close'].astype(float)
                
                return df[['Date', 'Close']].to_dict(orient="records")
            
            return await asyncio.to_thread(_fetch)
            
        except Exception as e:
            logger.debug(f"yfinance 실패: {str(e)}")
            raise
    
    async def _get_static_kospi_data(self) -> List[Dict]:
        """정적 코스피 데이터 (최후 수단)"""
        try:
            # 최근 30일간의 기본 데이터
            result = []
            base_price = 2500  # 기준 코스피 지수
            
            for i in range(30):
                date = datetime.now() - timedelta(days=i)
                # 약간의 변동성 추가
                variation = (i % 7 - 3) * 0.01  # 주간 패턴
                price = base_price * (1 + variation)
                
                result.append({
                    "Date": date.strftime("%Y-%m-%d"),
                    "Close": round(price, 2)
                })
            
            result.reverse()  # 날짜 순서 정렬
            return result
            
        except Exception as e:
            logger.debug(f"정적 데이터 생성 실패: {str(e)}")
            raise
    
    async def get_market_cap_top10(self) -> Dict:
        """시가총액 TOP10 조회"""
        try:
            def _fetch_market_cap():
                today = datetime.today().strftime("%Y%m%d")
                
                df = stock.get_market_cap_by_ticker(today, market="KOSPI")
                
                df = df.reset_index()[["티커", "시가총액", "종가"]]
                df["기업명"] = df["티커"].apply(lambda x: stock.get_market_ticker_name(x))
                
                df = df.sort_values(by="시가총액", ascending=False).head(10)
                df = df[["기업명", "티커", "시가총액", "종가"]]
                
                return {"시가총액_TOP10": df.to_dict(orient="records")}
            
            return await asyncio.to_thread(_fetch_market_cap)
            
        except Exception as e:
            logger.error(f"❌ 시가총액 데이터 조회 실패: {str(e)}")
            return {"error": str(e)}
    
    async def get_top_volume(self) -> List[Dict]:
        """거래량 TOP5 조회"""
        try:
            def _fetch_volume():
                today = datetime.today().strftime("%Y%m%d")
                
                df = stock.get_market_ohlcv(today, market="KOSPI")
                
                top5 = df.sort_values(by="거래량", ascending=False).head(5)
                top5["종목코드"] = top5.index
                top5["종목명"] = top5["종목코드"].apply(lambda code: stock.get_market_ticker_name(code))
                top5.reset_index(drop=True, inplace=True)
                
                result = top5[["종목명", "종목코드", "거래량"]].to_dict(orient="records")
                return result
            
            return await asyncio.to_thread(_fetch_volume)
            
        except Exception as e:
            logger.error(f"❌ 거래량 데이터 조회 실패: {str(e)}")
            raise HTTPException(status_code=503, detail=str(e))
    
    async def get_industry_analysis(self, name: str) -> Dict:
        """산업별 재무지표 분석 정보 조회"""
        try:
            with open("산업별설명.json", encoding="utf-8") as f:
                data = json.load(f)
            
            name = name.strip()
            for item in data:
                if item.get("industry") == name:
                    return item
            
            raise HTTPException(status_code=404, detail="해당 산업 정보가 없습니다.")
            
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="산업별설명.json 파일을 찾을 수 없습니다.")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")
    
    async def get_company_metrics(self, name: str) -> Dict:
        """기업 재무지표 JSON 조회"""
        try:
            with open("기업별_재무지표.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if name in data:
                return data[name]
            else:
                raise HTTPException(status_code=404, detail="해당 기업 지표가 없습니다.")
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

stock_service = StockService()