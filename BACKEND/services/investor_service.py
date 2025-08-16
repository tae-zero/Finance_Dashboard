import asyncio
import logging
from pykrx import stock
from datetime import datetime, timedelta
from typing import List, Dict
import json

logger = logging.getLogger("investor_service")

class InvestorService:
    def __init__(self):
        pass
    
    async def get_kospi_investor_value(self):
        """코스피 투자자별 매수/매도량 분석 (별칭 메서드)"""
        return await self.get_kospi_investor_value_impl()
    
    async def get_kospi_investor_value_impl(self):
        """코스피 투자자별 매수/매도량 분석 (구현)"""
        try:
            def _fetch_investor_data():
                today = datetime.today().strftime("%Y%m%d")
                yesterday = (datetime.today() - timedelta(days=1)).strftime("%Y%m%d")
                
                # 투자자별 거래량 데이터 조회 (포지셔널 인자 사용)
                df = stock.get_market_trading_value_by_investor(
                    yesterday,  # fromdate
                    today,      # todate
                    "KOSPI"     # market (포지셔널)
                )
                
                if df.empty:
                    return {"error": "투자자 데이터가 없습니다"}
                
                # 데이터 정리
                result = []
                for date in df.index:
                    daily_data = {
                        "date": date.strftime("%Y-%m-%d"),
                        "individual": int(df.loc[date, "개인"]),
                        "foreign": int(df.loc[date, "외국인"]),
                        "institution": int(df.loc[date, "기관"]),
                        "financial": int(df.loc[date, "금융투자"]),
                        "insurance": int(df.loc[date, "보험"]),
                        "investment": int(df.loc[date, "투신"]),
                        "bank": int(df.loc[date, "은행"]),
                        "pension": int(df.loc[date, "연기금"]),
                        "other": int(df.loc[date, "기타법인"])
                    }
                    result.append(daily_data)
                
                return {"투자자별_거래량": result}
            
            return await asyncio.to_thread(_fetch_investor_data)
            
        except Exception as e:
            logger.error(f"❌ 투자자 데이터 조회 실패: {str(e)}")
            return {"error": str(e)}
    
    async def get_investor_summary(self, ticker: str):
        """기업별 투자자 거래량 분석"""
        try:
            def _fetch_summary():
                today = datetime.today().strftime("%Y%m%d")
                yesterday = (datetime.today() - timedelta(days=1)).strftime("%Y%m%d")
                
                # 투자자별 거래량 (포지셔널 인자 사용)
                df = stock.get_market_trading_value_by_investor(
                    yesterday,  # fromdate
                    today,      # todate
                    ticker      # ticker (포지셔널)
                )
                
                if df.empty:
                    return {"error": "투자자 요약 데이터가 없습니다"}
                
                # 최신 데이터
                latest = df.iloc[-1]
                
                result = {
                    "ticker": ticker,
                    "date": latest.name.strftime("%Y-%m-%d"),
                    "individual": int(latest["개인"]),
                    "foreign": int(latest["외국인"]),
                    "institution": int(latest["기관"]),
                    "total": int(latest.sum())
                }
                
                return result
            
            return await asyncio.to_thread(_fetch_summary)
            
        except Exception as e:
            logger.error(f"❌ 투자자 요약 조회 실패 ({ticker}): {str(e)}")
            return {"error": str(e)}
    
    async def get_investor_trends(self, days: int = 30):
        """투자자 트렌드 분석"""
        try:
            def _fetch_trends():
                end_date = datetime.today()
                start_date = end_date - timedelta(days=days)
                
                df = stock.get_market_trading_value_by_investor(
                    start_date.strftime("%Y%m%d"),  # fromdate
                    end_date.strftime("%Y%m%d"),    # todate
                    "KOSPI"                         # market (포지셔널)
                )
                
                if df.empty:
                    return {"error": "트렌드 데이터가 없습니다"}
                
                # 주요 투자자별 트렌드
                trends = {
                    "individual": df["개인"].tolist(),
                    "foreign": df["외국인"].tolist(),
                    "institution": df["기관"].tolist(),
                    "dates": [d.strftime("%Y-%m-%d") for d in df.index]
                }
                
                return {"투자자_트렌드": trends}
            
            return await asyncio.to_thread(_fetch_trends)
            
        except Exception as e:
            logger.error(f"❌ 투자자 트렌드 조회 실패: {str(e)}")
            return {"error": str(e)}
    
    async def get_top_rankings(self):
        """매출액, DPS, 영업이익률 상위 5개 조회"""
        try:
            def _fetch_rankings():
                today = datetime.today().strftime("%Y%m%d")
                
                # 시가총액 상위 종목
                market_cap_df = stock.get_market_cap_by_ticker(today, "KOSPI")  # 포지셔널 인자
                
                # 거래량 상위 종목
                volume_df = stock.get_market_ohlcv(today, "KOSPI")  # 포지셔널 인자
                
                result = {
                    "시가총액_TOP5": [
                        {
                            "종목코드": ticker,
                            "종목명": stock.get_market_ticker_name(ticker),
                            "시가총액": int(row['시가총액'] / 100000000)  # 억원 단위
                        }
                        for ticker, row in market_cap_df.nlargest(5, '시가총액').iterrows()
                    ],
                    "거래량_TOP5": [
                        {
                            "종목코드": ticker,
                            "종목명": stock.get_market_ticker_name(ticker),
                            "거래량": int(row['거래량'])
                        }
                        for ticker, row in volume_df.nlargest(5, '거래량').iterrows()
                    ]
                }
                
                return result
            
            return await asyncio.to_thread(_fetch_rankings)
            
        except Exception as e:
            logger.error(f"❌ TOP 랭킹 조회 실패: {str(e)}")
            return {"error": str(e)}

investor_service = InvestorService()
