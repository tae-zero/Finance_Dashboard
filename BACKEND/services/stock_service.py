import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from pykrx import stock
from fastapi import HTTPException
import time
import random
from typing import Dict, List, Optional

def retry_on_failure(max_retries=3, delay=1):
    """재시도 데코레이터"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        print(f"❌ {func.__name__} 실패: {str(e)}")
                        raise e
                    time.sleep(delay + random.random())
            return None
        return wrapper
    return decorator

class StockService:
    def __init__(self):
        self.today = datetime.now()
        self.start_date = (self.today - timedelta(days=365)).strftime('%Y%m%d')
        self.end_date = self.today.strftime('%Y%m%d')

    @retry_on_failure(max_retries=3)
    def get_stock_price(self, ticker: str) -> Dict:
        """주가 데이터 조회"""
        try:
            # yfinance에서 데이터 가져오기
            stock_data = yf.download(ticker, 
                                   start=(self.today - timedelta(days=365)).strftime('%Y-%m-%d'),
                                   end=self.today.strftime('%Y-%m-%d'),
                                   progress=False)
            
            if stock_data.empty:
                return {"error": "데이터 없음"}
            
            # 데이터 포맷팅
            stock_data = stock_data.reset_index()
            stock_data['Date'] = stock_data['Date'].dt.strftime('%Y-%m-%d')
            
            return {
                "dates": stock_data['Date'].tolist(),
                "prices": stock_data['Close'].round(2).tolist(),
                "volumes": stock_data['Volume'].tolist()
            }
            
        except Exception as e:
            print(f"❌ 주가 데이터 조회 실패: {e}")
            return {"error": "데이터 조회 실패"}

    @retry_on_failure(max_retries=3)
    def get_investor_data(self, code: str) -> Dict:
        """투자자 데이터 조회"""
        try:
            # pykrx에서 데이터 가져오기
            df = stock.get_market_trading_value_by_date(
                fromdate=self.start_date,
                todate=self.end_date,
                ticker=code
            )
            
            if df.empty:
                return {"error": "조회된 데이터가 없습니다."}
            
            # 데이터 포맷팅
            df = df.reset_index()
            df['날짜'] = df['날짜'].dt.strftime('%Y-%m-%d')
            
            return {
                "dates": df['날짜'].tolist(),
                "개인": df['개인'].astype(float).round(2).tolist(),
                "외국인": df['외국인'].astype(float).round(2).tolist(),
                "기관": df['기관'].astype(float).round(2).tolist()
            }
            
        except Exception as e:
            print(f"❌ 투자자 데이터 조회 실패: {e}")
            return {"error": "데이터 조회 실패"}

    @retry_on_failure(max_retries=3)
    def get_market_cap_top10(self) -> List[Dict]:
        """시가총액 상위 10개 기업 조회"""
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
            
            return result
            
        except Exception as e:
            print(f"❌ 시가총액 데이터 조회 실패: {e}")
            return []

    @retry_on_failure(max_retries=3)
    def get_kospi_index(self) -> Dict:
        """코스피 지수 조회"""
        try:
            df = stock.get_index_ohlcv_by_date(
                self.start_date,
                self.end_date,
                "1001"  # KOSPI 지수
            )
            
            if df.empty:
                return {"error": "데이터 없음"}
            
            df = df.reset_index()
            df['날짜'] = df['날짜'].dt.strftime('%Y-%m-%d')
            
            return {
                "dates": df['날짜'].tolist(),
                "values": df['종가'].astype(float).round(2).tolist(),
                "volumes": df['거래량'].tolist()
            }
            
        except Exception as e:
            print(f"❌ 코스피 지수 조회 실패: {e}")
            return {"error": "데이터 조회 실패"}