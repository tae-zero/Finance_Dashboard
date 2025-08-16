import datetime as dt
import logging
import time
from typing import List, Optional, Dict
from fastapi import HTTPException
import asyncio

from requests.exceptions import JSONDecodeError as ReqJSONDecodeError, RequestException

# 외부 데이터 소스
from pykrx import stock
import yfinance as yf


logger = logging.getLogger(__name__)

class StockService:
    def __init__(self):
        self.KOSPI_TICKER = "1001"  # KOSPI 지수 코드 상수
        self._setup_logging_levels()
    
    def _setup_logging_levels(self):
        """외부 라이브러리 로깅 레벨 설정"""
        try:
            # 외부 라이브러리 로깅 레벨을 WARNING으로 설정
            logging.getLogger("yfinance").setLevel(logging.WARNING)
            logging.getLogger("urllib3").setLevel(logging.WARNING)
            logging.getLogger("pykrx").setLevel(logging.WARNING)
            logging.getLogger("requests").setLevel(logging.WARNING)
            logger.info("✅ 외부 라이브러리 로깅 레벨 설정 완료")
        except Exception as e:
            logger.debug("⚠️ 로깅 레벨 설정 실패: %s", e)
    
    def _get_index_ohlcv_safe(self, ticker: str, start: str, end: str):
        """
        pykrx가 간헐적으로 빈 응답/HTML을 주며 JSONDecodeError를 터뜨리는 것을 방어.
        호출 구간만 root 로그 레벨을 WARNING으로 올려 pykrx 내부의 잘못된 logging.info 포맷도 회피.
        """
        root = logging.getLogger()
        prev_level = root.level
        try:
            root.setLevel(logging.WARNING)  # pykrx 내부 잘못된 info 호출 회피
            for i in range(3):
                try:
                    df = stock.get_index_ohlcv_by_date(fromdate=start, todate=end, ticker=ticker)
                    if df is not None and not df.empty:
                        return df
                    raise ValueError("pykrx returned empty DataFrame")
                except (ReqJSONDecodeError, ValueError, RequestException) as e:
                    logger.warning("pykrx 실패(%s) - 재시도 %d/3: %s", ticker, i + 1, e)
                    time.sleep(0.7 * (i + 1))
            return None
        finally:
            root.setLevel(prev_level)
    
    def _yf_series(self, symbol: str, period: str = "1y", interval: str = "1d") -> Optional[List[Dict]]:
        try:
            df = yf.download(
                symbol,
                period=period,
                interval=interval,
                group_by="ticker",
                auto_adjust=False,
                progress=False,
                threads=False,
            )
            if df is None or df.empty:
                return None
            df = df.reset_index()
            out = []
            for d, c in zip(df["Date"], df["Close"]):
                if c is None:
                    continue
                d = d.strftime("%Y-%m-%d") if hasattr(d, "strftime") else str(d)
                out.append({"Date": d, "Close": float(c)})
            return out
        except Exception as e:
            logger.warning("yfinance 실패(%s): %s", symbol, e)
            return None
    
    async def get_stock_price(self, ticker: str, period: str = "3y") -> List[Dict]:
        """주식 가격 데이터 조회"""
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
            logger.error("주가 데이터 조회 실패 (%s): %s", ticker, str(e))
            return {"error": str(e)}
    
    async def get_kospi_data(self) -> List[Dict]:
        """코스피 지수 데이터 조회 (다단 폴백 시스템)"""
        today = dt.date.today()
        start_d = today - dt.timedelta(days=365)
        
        # 1차 시도: pykrx (안전한 재시도)
        try:
            start = start_d.strftime("%Y%m%d")
            end = today.strftime("%Y%m%d")
            df = await asyncio.to_thread(
                self._get_index_ohlcv_safe, 
                self.KOSPI_TICKER, 
                start, 
                end
            )
            if df is not None and not df.empty:
                df = df.reset_index()
                result = [
                    {"Date": d.strftime("%Y-%m-%d"), "Close": float(c)}
                    for d, c in zip(df.index, df["종가"])
                    if c is not None
                ]
                if result:
                    logger.info("✅ pykrx로 코스피 데이터 조회 성공")
                    return result
        except Exception as e:
            logger.debug("⚠️ pykrx 실패: %s", str(e))
        
        # 2차 시도: yfinance (안전한 다운로드)
        try:
            result = await asyncio.to_thread(
                self._yf_series, 
                "^KS11", 
                "1y", 
                "1d"
            )
            if result and len(result) > 0:
                logger.info("✅ yfinance로 코스피 데이터 조회 성공")
                return result
        except Exception as e:
            logger.debug("⚠️ yfinance 실패: %s", str(e))
        
        # 3차 시도: 정적 데이터 (최후 수단)
        try:
            result = await self._get_static_kospi_data()
            if result and len(result) > 0:
                logger.info("✅ 정적 데이터로 코스피 데이터 조회 성공")
                return result
        except Exception as e:
            logger.debug("⚠️ 정적 데이터 실패: %s", str(e))
        
        # 모든 방법 실패
        logger.error("❌ 모든 코스피 데이터 조회 방법 실패")
        raise HTTPException(status_code=503, detail="코스피 데이터 조회 완전 실패")
    
    async def _get_static_kospi_data(self) -> List[Dict]:
        """정적 코스피 데이터 (최후 수단)"""
        try:
            # 최근 30일간의 기본 데이터
            result = []
            base_price = 2500  # 기준 코스피 지수
            
            for i in range(30):
                date = dt.datetime.now() - dt.timedelta(days=i)
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
            logger.debug("정적 데이터 생성 실패: %s", str(e))
            raise
    
    async def get_market_cap_top10(self) -> Dict:
        """시가총액 TOP10 조회"""
        try:
            def _fetch_market_cap():
                today = dt.datetime.today().strftime("%Y%m%d")
                
                df = stock.get_market_cap_by_ticker(today, market="KOSPI")
                
                df = df.reset_index()[["티커", "시가총액", "종가"]]
                df["기업명"] = df["티커"].apply(lambda x: stock.get_market_ticker_name(x))
                
                df = df.sort_values(by="시가총액", ascending=False).head(10)
                df = df[["기업명", "티커", "시가총액", "종가"]]
                
                return {"시가총액_TOP10": df.to_dict(orient="records")}
            
            return await asyncio.to_thread(_fetch_market_cap)
            
        except Exception as e:
            logger.error("❌ 시가총액 데이터 조회 실패: %s", str(e))
            return {"error": str(e)}
    
    async def get_top_volume(self) -> List[Dict]:
        """거래량 TOP5 조회"""
        try:
            def _fetch_volume():
                today = dt.datetime.today().strftime("%Y%m%d")
                
                df = stock.get_market_ohlcv(today, market="KOSPI")
                
                top5 = df.sort_values(by="거래량", ascending=False).head(5)
                top5["종목코드"] = top5.index
                top5["종목명"] = top5["종목코드"].apply(lambda code: stock.get_market_ticker_name(code))
                top5.reset_index(drop=True, inplace=True)
                
                result = top5[["종목명", "종목코드", "거래량"]].to_dict(orient="records")
                return result
            
            return await asyncio.to_thread(_fetch_volume)
            
        except Exception as e:
            logger.error("❌ 거래량 데이터 조회 실패: %s", str(e))
            raise HTTPException(status_code=503, detail=str(e))
    
    async def get_industry_analysis(self, name: str) -> Dict:
        """산업별 재무지표 분석 정보 조회"""
        try:
            with open("산업별설명.json", encoding="utf-8") as f:
                import json
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
                import json
                data = json.load(f)
            
            if name in data:
                return data[name]
            else:
                raise HTTPException(status_code=404, detail="해당 기업 지표가 없습니다.")
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


stock_service = StockService()