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
import json

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
        """주가 데이터 조회 - 실패시 더미 데이터 반환"""
        cache_key = f"stock_price_{ticker}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data

        try:
            # 더미 데이터 생성
            dummy_data = {
                "dates": [
                    (self.today - timedelta(days=i)).strftime('%Y-%m-%d')
                    for i in range(30, 0, -1)
                ],
                "prices": [
                    round(random.uniform(50000, 70000), 2)
                    for _ in range(30)
                ],
                "volumes": [
                    random.randint(500000, 1500000)
                    for _ in range(30)
                ],
                "is_dummy": True
            }
            
            self._set_cached_data(cache_key, dummy_data)
            return dummy_data
            
        except Exception as e:
            logger.error(f"주가 데이터 조회 실패: {e}", exc_info=True)
            raise HTTPException(status_code=503, detail=f"주가 데이터 조회 실패: {str(e)}")

    async def get_kospi_index(self) -> Dict:
        """코스피 지수 조회 - 실패시 더미 데이터 반환"""
        cache_key = "kospi_index"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data

        try:
            # 더미 데이터 생성
            dummy_data = {
                "dates": [
                    (self.today - timedelta(days=i)).strftime('%Y-%m-%d')
                    for i in range(30, 0, -1)
                ],
                "values": [
                    round(random.uniform(2400, 2600), 2)
                    for _ in range(30)
                ],
                "volumes": [
                    random.randint(500000000, 1000000000)
                    for _ in range(30)
                ],
                "is_dummy": True
            }
            
            self._set_cached_data(cache_key, dummy_data)
            return dummy_data
            
        except Exception as e:
            logger.error(f"코스피 지수 조회 실패: {e}", exc_info=True)
            raise HTTPException(status_code=503, detail=f"코스피 지수 조회 실패: {str(e)}")

    def get_market_cap_top10(self) -> List[Dict]:
        """시가총액 상위 10개 기업 조회 - 실패시 더미 데이터 반환"""
        cache_key = "market_cap_top10"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data

        try:
            # 더미 데이터
            dummy_data = [
                {"종목코드": "005930", "기업명": "삼성전자", "시가총액": 450000},
                {"종목코드": "000660", "기업명": "SK하이닉스", "시가총액": 120000},
                {"종목코드": "005935", "기업명": "삼성전자우", "시가총액": 100000},
                {"종목코드": "005380", "기업명": "현대차", "시가총액": 90000},
                {"종목코드": "000270", "기업명": "기아", "시가총액": 85000},
                {"종목코드": "051910", "기업명": "LG화학", "시가총액": 80000},
                {"종목코드": "035420", "기업명": "NAVER", "시가총액": 75000},
                {"종목코드": "005490", "기업명": "POSCO홀딩스", "시가총액": 70000},
                {"종목코드": "035720", "기업명": "카카오", "시가총액": 65000},
                {"종목코드": "006400", "기업명": "삼성SDI", "시가총액": 60000}
            ]
            
            self._set_cached_data(cache_key, dummy_data)
            return dummy_data
            
        except Exception as e:
            logger.error(f"시가총액 데이터 조회 실패: {e}", exc_info=True)
            raise HTTPException(status_code=503, detail=f"시가총액 데이터 조회 실패: {str(e)}")

    def get_volume_top5(self) -> List[Dict]:
        """거래량 상위 5개 기업 조회"""
        try:
            # 더미 데이터
            return [
                {"종목코드": "005930", "기업명": "삼성전자", "거래량": 15000000},
                {"종목코드": "000660", "기업명": "SK하이닉스", "거래량": 8000000},
                {"종목코드": "035720", "기업명": "카카오", "거래량": 5000000},
                {"종목코드": "035420", "기업명": "NAVER", "거래량": 3000000},
                {"종목코드": "005380", "기업명": "현대차", "거래량": 2000000}
            ]
        except Exception as e:
            logger.error(f"거래량 데이터 조회 실패: {e}", exc_info=True)
            raise HTTPException(status_code=503, detail=f"거래량 데이터 조회 실패: {str(e)}")