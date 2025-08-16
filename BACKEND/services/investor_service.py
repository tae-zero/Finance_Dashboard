from pykrx import stock
from utils.data_processor import DataProcessor
from fastapi import HTTPException
from typing import List, Dict, Optional

class InvestorService:
    def __init__(self):
        self.data_processor = DataProcessor()
    
    def get_investor_summary(self, ticker: str) -> List[Dict]:
        """투자자별 거래 동향 요약"""
        try:
            # pykrx를 사용한 투자자 데이터 조회
            investor_data = self.data_processor.get_investor_data(ticker)
            return investor_data
        except Exception as e:
            print(f"❌ 투자자 데이터 조회 실패: {e}")
            return {"error": "조회된 데이터가 없습니다."}
    
    def get_institutional_trading(self, ticker: str) -> Dict:
        """기관 투자자 거래 동향"""
        try:
            # 기관 투자자 데이터 조회
            institutional_data = self.data_processor.get_institutional_data(ticker)
            return institutional_data
        except Exception as e:
            print(f"❌ 기관 투자자 데이터 조회 실패: {e}")
            return {"error": "데이터 없음"}
    
    def get_foreign_investor_trading(self, ticker: str) -> Dict:
        """외국인 투자자 거래 동향"""
        try:
            # 외국인 투자자 데이터 조회
            foreign_data = self.data_processor.get_foreign_data(ticker)
            return foreign_data
        except Exception as e:
            print(f"❌ 외국인 투자자 데이터 조회 실패: {e}")
            return {"error": "데이터 없음"}
