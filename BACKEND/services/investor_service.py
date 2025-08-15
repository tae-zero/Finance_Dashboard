from pykrx.stock import get_market_trading_volume_by_date, get_market_trading_value_by_investor
from datetime import datetime, timedelta
from fastapi import HTTPException
from typing import List, Dict
from utils.database import db_manager
from utils.data_processor import DataProcessor

class InvestorService:
    def __init__(self):
        self.data_processor = DataProcessor()
        self.collection = db_manager.collection
    
    def get_investor_summary(self, ticker: str) -> List[Dict]:
        """기업별 투자자 거래량 분석"""
        try:
            # 기간 설정: 오늘 ~ 10일 전
            end = datetime.today()
            start = end - timedelta(days=10)
            
            # 날짜 포맷
            start_str = start.strftime("%Y%m%d")
            end_str = end.strftime("%Y%m%d")
            
            # 데이터 조회
            df = get_market_trading_volume_by_date(start_str, end_str, ticker)
            
            if df.empty:
                return {"error": "조회된 데이터가 없습니다."}
            
            # 날짜 인덱스를 컬럼으로
            df.reset_index(inplace=True)
            df.rename(columns={"날짜": "date"}, inplace=True)
            
            # 기타법인 컬럼 제거 (있을 경우)
            remove_cols = ["기타법인"]
            for col in remove_cols:
                if col in df.columns:
                    df.drop(columns=[col], inplace=True)
            
            # 숫자형 변환
            for col in df.columns:
                if col != "date":
                    df[col] = df[col].astype(int)
            
            # JSON 변환
            return df.to_dict(orient="records")
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_kospi_investor_value(self) -> List[Dict]:
        """코스피 투자자별 매수/매도량 분석"""
        try:
            # 최근 10일 날짜 계산
            end_date = datetime.today()
            start_date = end_date - timedelta(days=10)
            
            start = start_date.strftime("%Y%m%d")
            end = end_date.strftime("%Y%m%d")
            
            # pykrx 데이터
            df = get_market_trading_value_by_investor(start, end, "KOSPI")
            
            # 날짜 인덱스가 맞는지 확인하고 변환
            try:
                df.index = pd.to_datetime(df.index, format="%Y%m%d")
                df.index = df.index.strftime('%Y-%m-%d')
                df = df.reset_index(names="날짜")
            except:
                df = df.reset_index()  # fallback
            
            return df.to_dict(orient="records")
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_top_rankings(self) -> Dict:
        """매출액, DPS, 영업이익률 상위 5개 조회"""
        try:
            # MongoDB에서 필요한 데이터만 조회
            cursor = self.collection.find({
                "지표.2024/12_매출액": {"$exists": True},
                "지표.2024/12_DPS": {"$exists": True},
                "지표.2024/12_영업이익률": {"$exists": True}
            }, {
                "기업명": 1,
                "지표.2024/12_매출액": 1,
                "지표.2024/12_DPS": 1,
                "지표.2024/12_영업이익률": 1
            })
            
            # 데이터 정규화
            df = self.data_processor.normalize_mongodb_data(cursor, {
                "기업명": "기업명",
                "지표.2024/12_매출액": "매출액",
                "지표.2024/12_DPS": "DPS",
                "지표.2024/12_영업이익률": "영업이익률"
            })
            
            if df.empty:
                return {"error": "순위 데이터가 없습니다."}
            
            # 상위 순위 추출
            result = self.data_processor.extract_top_rankings(
                df, ["매출액", "DPS", "영업이익률"], top_n=5
            )
            
            return result
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_investor_trends(self, days: int = 30) -> Dict:
        """투자자 트렌드 분석"""
        try:
            # 최근 N일간의 투자자별 거래량 변화 분석
            end_date = datetime.today()
            start_date = end_date - timedelta(days=days)
            
            start = start_date.strftime("%Y%m%d")
            end = end_date.strftime("%Y%m%d")
            
            # 투자자별 거래량 데이터
            volume_df = get_market_trading_volume_by_date(start, end, "005930")  # 삼성전자 기준
            
            # 투자자별 거래대금 데이터
            value_df = get_market_trading_value_by_investor(start, end, "KOSPI")
            
            # 데이터 전처리
            volume_df.reset_index(inplace=True)
            value_df.reset_index(inplace=True)
            
            # 결과 구성
            result = {
                "거래량_트렌드": volume_df.to_dict(orient="records"),
                "거래대금_트렌드": value_df.to_dict(orient="records"),
                "분석_기간": f"{start} ~ {end}"
            }
            
            return result
            
        except Exception as e:
            return {"error": str(e)}
