import yfinance as yf
from pykrx import stock
import pandas as pd
from datetime import datetime, timedelta
import time
import logging
import requests
from typing import Dict, List, Optional
from fastapi import HTTPException
import asyncio
from functools import wraps
import aiohttp

logger = logging.getLogger("data_processor")

def circuit_breaker(max_failures: int = 3, reset_time: int = 60):
    """회로 차단기 데코레이터"""
    def decorator(func):
        failures = 0
        last_failure_time = 0

        @wraps(func)
        async def wrapper(*args, **kwargs):
            nonlocal failures, last_failure_time
            
            # 실패 횟수 초기화 체크
            if time.time() - last_failure_time > reset_time:
                failures = 0

            # 회로 차단 체크
            if failures >= max_failures:
                if time.time() - last_failure_time <= reset_time:
                    raise HTTPException(
                        status_code=503,
                        detail="서비스가 일시적으로 불안정합니다. 잠시 후 다시 시도해주세요."
                    )
                failures = 0

            try:
                return await func(*args, **kwargs)
            except Exception as e:
                failures += 1
                last_failure_time = time.time()
                raise e

        return wrapper
    return decorator

class DataProcessor:
    def __init__(self):
        self.today = datetime.now()
        self.start_date = (self.today - timedelta(days=365)).strftime('%Y%m%d')
        self.end_date = self.today.strftime('%Y%m%d')
        self._cache = {}
        self.CACHE_DURATION = 600  # 10분
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def _get_cached_data(self, key: str) -> Optional[Dict]:
        """캐시된 데이터 조회"""
        if key in self._cache:
            timestamp, data = self._cache[key]
            if time.time() - timestamp < self.CACHE_DURATION:
                return data
        return None

    def _set_cached_data(self, key: str, data: Dict):
        """데이터 캐시에 저장"""
        self._cache[key] = (time.time(), data)

    async def _async_request(self, url: str, timeout: int = 10) -> Dict:
        """비동기 HTTP 요청"""
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers, timeout=timeout) as response:
                response.raise_for_status()
                return await response.json()

    @circuit_breaker(max_failures=3, reset_time=60)
    async def get_stock_data(self, ticker: str) -> Dict:
        """주식 데이터 조회 (yfinance)"""
        cache_key = f"stock_data_{ticker}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data

        try:
            # yfinance 호출을 비동기 컨텍스트로 이동
            def _fetch_stock():
                stock = yf.Ticker(ticker)
                hist = stock.history(period="1y")
                if hist.empty:
                    raise ValueError("데이터가 비어있습니다")
                return hist

            hist = await asyncio.to_thread(_fetch_stock)

            data = {
                "dates": hist.index.strftime('%Y-%m-%d').tolist(),
                "prices": hist['Close'].round(2).tolist(),
                "volumes": hist['Volume'].tolist()
            }
            
            self._set_cached_data(cache_key, data)
            return data
            
        except Exception as e:
            logger.error(f"주식 데이터 조회 실패 ({ticker}): {str(e)}")
            # 마지막 성공 데이터 반환 시도
            last_data = self._get_cached_data(cache_key)
            if last_data:
                logger.info(f"캐시된 마지막 데이터 반환 ({ticker})")
                return last_data
            raise HTTPException(status_code=503, detail=f"주식 데이터 조회 실패: {str(e)}")

    @circuit_breaker(max_failures=3, reset_time=60)
    async def get_kospi_data(self) -> Dict:
        """코스피 지수 데이터 조회 (pykrx)"""
        cache_key = "kospi_data"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data

        try:
            # pykrx 호출을 비동기 컨텍스트로 이동
            def _fetch_kospi():
                df = stock.get_index_ohlcv_by_date(
                    self.start_date,
                    self.end_date,
                    "1001"
                )
                if df.empty:
                    raise ValueError("데이터가 비어있습니다")
                return df

            df = await asyncio.to_thread(_fetch_kospi)

            data = {
                "dates": df.index.strftime('%Y-%m-%d').tolist(),
                "values": df['종가'].astype(float).round(2).tolist(),
                "volumes": df['거래량'].tolist()
            }
            
            self._set_cached_data(cache_key, data)
            return data
            
        except Exception as e:
            logger.error(f"코스피 데이터 조회 실패: {str(e)}")
            # 마지막 성공 데이터 반환 시도
            last_data = self._get_cached_data(cache_key)
            if last_data:
                logger.info("캐시된 마지막 코스피 데이터 반환")
                return last_data
            raise HTTPException(status_code=503, detail=f"코스피 데이터 조회 실패: {str(e)}")

    @circuit_breaker(max_failures=3, reset_time=60)
    async def get_market_cap_data(self) -> List[Dict]:
        """시가총액 데이터 조회"""
        cache_key = "market_cap_data"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data

        try:
            # pykrx 호출을 비동기 컨텍스트로 이동
            def _fetch_market_cap():
                df = stock.get_market_cap_by_ticker(self.today.strftime("%Y%m%d"))
                top10 = df.nlargest(10, '시가총액')
                
                result = []
                for ticker in top10.index:
                    try:
                        company_name = stock.get_market_ticker_name(ticker)
                        market_cap = int(top10.loc[ticker, '시가총액'] / 100000000)
                        result.append({
                            "종목코드": ticker,
                            "기업명": company_name,
                            "시가총액": market_cap
                        })
                    except Exception as e:
                        logger.warning(f"기업 정보 조회 실패 ({ticker}): {str(e)}")
                        continue
                
                if not result:
                    raise ValueError("데이터가 비어있습니다")
                return result

            result = await asyncio.to_thread(_fetch_market_cap)
            
            self._set_cached_data(cache_key, result)
            return result
            
        except Exception as e:
            logger.error(f"시가총액 데이터 조회 실패: {str(e)}")
            # 마지막 성공 데이터 반환 시도
            last_data = self._get_cached_data(cache_key)
            if last_data:
                logger.info("캐시된 마지막 시가총액 데이터 반환")
                return last_data
            raise HTTPException(status_code=503, detail=f"시가총액 데이터 조회 실패: {str(e)}")

# 싱글톤 인스턴스 생성
data_processor = DataProcessor()