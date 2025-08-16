import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from pykrx import stock
from fastapi import HTTPException
import time
import random
from typing import Dict, List, Optional
import logging
import asyncio
from functools import lru_cache

logger = logging.getLogger("stock_service")

# 캐시 설정
CACHE_DURATION = 600  # 10분
_cache = {}

class StockService:
    def __init__(self):
        self.today = datetime.now()
        self.start_date = (self.today - timedelta(days=365)).strftime('%Y%m%d')
        self.end_date = self.today.strftime('%Y%m%d')

    def _get_cached_data(self, key: str) -> Optional[Dict]:
        """캐시된 데이터 조회"""
        if key in _cache:
            timestamp, data = _cache[key]
            if time.time() - timestamp < CACHE_DURATION:
                return data
        return None

    def _set_cached_data(self, key: str, data: Dict):
        """데이터 캐시에 저장"""
        _cache[key] = (time.time(), data)

    async def get_stock_price(self, ticker: str) -> Dict:
        """주가 데이터 조회"""
        cache_key = f"stock_price_{ticker}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data

        try:
            for attempt in range(3):  # 최대 3번 재시도
                try:
                    stock_data = yf.download(
                        ticker,
                        start=(self.today - timedelta(days=365)).strftime('%Y-%m-%d'),
                        end=self.today.strftime('%Y-%m-%d'),
                        progress=False
                    )
                    
                    if stock_data.empty:
                        await asyncio.sleep(2 ** attempt)  # 지수 백오프
                        continue

                    # 데이터 포맷팅
                    stock_data = stock_data.reset_index()
                    stock_data['Date'] = stock_data['Date'].dt.strftime('%Y-%m-%d')
                    
                    result = {
                        "dates": stock_data['Date'].tolist(),
                        "prices": stock_data['Close'].round(2).tolist(),
                        "volumes": stock_data['Volume'].tolist()
                    }
                    
                    self._set_cached_data(cache_key, result)
                    return result
                    
                except Exception as e:
                    logger.warning(f"주가 데이터 조회 재시도 {attempt + 1}/3: {e}")
                    if attempt == 2:  # 마지막 시도에서 실패
                        raise HTTPException(status_code=503, detail=f"주가 데이터 조회 실패: {str(e)}")
                    await asyncio.sleep(2 ** attempt)  # 지수 백오프
                    
        except Exception as e:
            logger.error(f"주가 데이터 조회 실패: {e}", exc_info=True)
            # 캐시된 데이터가 있으면 오래된 데이터라도 반환
            old_data = self._get_cached_data(cache_key)
            if old_data:
                logger.info(f"캐시된 이전 데이터 반환: {ticker}")
                return {**old_data, "cached": True}
            raise HTTPException(status_code=503, detail=f"주가 데이터 조회 실패: {str(e)}")

    async def get_kospi_index(self) -> Dict:
        """코스피 지수 조회"""
        cache_key = "kospi_index"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data

        try:
            for attempt in range(3):
                try:
                    df = stock.get_index_ohlcv_by_date(
                        self.start_date,
                        self.end_date,
                        "1001"
                    )
                    
                    if df.empty:
                        await asyncio.sleep(2 ** attempt)
                        continue
                        
                    df = df.reset_index()
                    df['날짜'] = df['날짜'].dt.strftime('%Y-%m-%d')
                    
                    result = {
                        "dates": df['날짜'].tolist(),
                        "values": df['종가'].astype(float).round(2).tolist(),
                        "volumes": df['거래량'].tolist()
                    }
                    
                    self._set_cached_data(cache_key, result)
                    return result
                    
                except Exception as e:
                    logger.warning(f"코스피 지수 조회 재시도 {attempt + 1}/3: {e}")
                    if attempt == 2:
                        raise HTTPException(status_code=503, detail=f"코스피 지수 조회 실패: {str(e)}")
                    await asyncio.sleep(2 ** attempt)
                    
        except Exception as e:
            logger.error(f"코스피 지수 조회 실패: {e}", exc_info=True)
            old_data = self._get_cached_data(cache_key)
            if old_data:
                logger.info("캐시된 이전 코스피 데이터 반환")
                return {**old_data, "cached": True}
            raise HTTPException(status_code=503, detail=f"코스피 지수 조회 실패: {str(e)}")

    def get_market_cap_top10(self) -> List[Dict]:
        """시가총액 상위 10개 기업 조회"""
        cache_key = "market_cap_top10"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data

        try:
            df = stock.get_market_cap_by_ticker(self.today.strftime("%Y%m%d"))
            top10 = df.nlargest(10, '시가총액')
            
            result = []
            for ticker in top10.index:
                company_name = stock.get_market_ticker_name(ticker)
                market_cap = int(top10.loc[ticker, '시가총액'] / 100000000)  # 억 원 단위
                result.append({
                    "종목코드": ticker,
                    "기업명": company_name,
                    "시가총액": market_cap
                })
            
            self._set_cached_data(cache_key, result)
            return result
            
        except Exception as e:
            logger.error(f"시가총액 데이터 조회 실패: {e}", exc_info=True)
            old_data = self._get_cached_data(cache_key)
            if old_data:
                logger.info("캐시된 이전 시가총액 데이터 반환")
                return old_data
            raise HTTPException(status_code=503, detail=f"시가총액 데이터 조회 실패: {str(e)}")