import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from pykrx import stock
from fastapi import HTTPException
from typing import List, Dict
from utils.data_processor import DataProcessor
import json
import asyncio
import logging

logger = logging.getLogger("stock_service")

class StockService:
    def __init__(self):
        self.data_processor = DataProcessor()
        self.KOSPI_TICKER = "1001"  # KOSPI 지수 코드 상수
    
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
        """코스피 지수 데이터 조회 (pykrx + yfinance 폴백)"""
        try:
            # 1차 시도: pykrx
            try:
                def _fetch_pykrx():
                    today = datetime.today().date()
                    yesterday = today - timedelta(days=1)
                    
                    df = stock.get_index_ohlcv_by_date(
                        yesterday.strftime('%Y%m%d'),
                        today.strftime('%Y%m%d'),
                        self.KOSPI_TICKER  # 상수 사용
                    )
                    
                    if df.empty:
                        raise ValueError("pykrx 데이터가 비어있습니다")
                    
                    df = df.reset_index()
                    df['Date'] = df.index.astype(str)
                    df['Close'] = df['종가'].astype(float)
                    
                    return df[['Date', 'Close']].to_dict(orient="records")
                
                result = await asyncio.to_thread(_fetch_pykrx)
                logger.info("✅ pykrx로 코스피 데이터 조회 성공")
                return result
                
            except Exception as pykrx_error:
                logger.warning(f"⚠️ pykrx 실패, yfinance로 폴백: {str(pykrx_error)}")
                
                # 2차 시도: yfinance
                def _fetch_yfinance():
                    df = yf.download("^KS11", period="1y", interval="1d", auto_adjust=True)
                    
                    if df.empty:
                        raise HTTPException(status_code=400, detail="yfinance 데이터가 없습니다")
                    
                    close_col = None
                    for col in df.columns:
                        if isinstance(col, tuple):
                            if "Close" in col:
                                close_col = col
                                break
                        elif col == "Close":
                            close_col = col
                            break
                    
                    if close_col is None:
                        raise HTTPException(status_code=400, detail=f"Close 컬럼이 없습니다. 컬럼 목록: {df.columns.tolist()}")
                    
                    df = df[[close_col]].reset_index()
                    df.columns = ['Date', 'Close']
                    df['Date'] = df['Date'].astype(str)
                    df['Close'] = df['Close'].astype(float)
                    
                    return df.to_dict(orient="records")
                
                result = await asyncio.to_thread(_fetch_yfinance)
                logger.info("✅ yfinance로 코스피 데이터 조회 성공")
                return result
                
        except Exception as e:
            logger.error(f"❌ 코스피 데이터 조회 완전 실패: {str(e)}")
            raise HTTPException(status_code=503, detail=f"코스피 데이터 조회 실패: {str(e)}")
    
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