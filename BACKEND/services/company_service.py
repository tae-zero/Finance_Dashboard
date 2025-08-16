from utils.database import db_manager
from utils.data_processor import DataProcessor
from fastapi import HTTPException
from typing import Dict, List, Optional

class CompanyService:
    def __init__(self):
        # db_manager.collection 대신 get_collection 메서드 사용
        self.collection = db_manager.get_collection("companies") if db_manager else None
        self.explain = db_manager.get_collection("explain") if db_manager else None
        self.outline = db_manager.get_collection("outline") if db_manager else None
    
    def get_company_data(self, name: str) -> Dict:
        """기업 상세 정보 조회"""
        if not self.collection:
            raise HTTPException(status_code=500, detail="데이터베이스 연결 실패")
        
        # 기본 정보 조회
        base = self.collection.find_one({"기업명": name}, {"_id": 0})
        
        if not base:
            raise HTTPException(status_code=404, detail="해당 기업을 찾을 수 없습니다.")
        
        # 기업 개요 조회
        outline = self.outline.find_one({"기업명": name}, {"_id": 0}) if self.outline else {}
        
        # 기업 설명 조회
        explain = self.explain.find_one({"기업명": name}, {"_id": 0}) if self.explain else {}
        
        # 데이터 병합
        result = {**base}
        if outline:
            result["개요"] = outline.get("개요", "")
        if explain:
            result["설명"] = explain.get("설명", "")
        
        return result
    
    def get_all_company_names(self) -> List[str]:
        """전체 기업명 목록 조회"""
        if not self.collection:
            raise HTTPException(status_code=500, detail="데이터베이스 연결 실패")
        
        cursor = self.collection.find({}, {"_id": 0, "기업명": 1})
        names = [doc["기업명"] for doc in cursor if "기업명" in doc]
        return names
    
    def get_company_metrics(self, name: str) -> Dict:
        """기업 재무지표 조회"""
        if not self.collection:
            raise HTTPException(status_code=500, detail="데이터베이스 연결 실패")
        
        # MongoDB에서 기업 지표 조회
        company_data = self.collection.find_one({"기업명": name}, {"_id": 0, "지표": 1})
        
        if not company_data:
            raise HTTPException(status_code=404, detail="해당 기업 지표가 없습니다.")
        
        # 실제 데이터 구조 확인을 위한 로그
        print(f"🔍 {name} 기업 지표 데이터 구조:", company_data.get("지표", {}))
        
        return company_data.get("지표", {})
    
    def get_sales_data(self, name: str) -> List[Dict]:
        """기업 매출 데이터 조회"""
        if not self.collection:
            raise HTTPException(status_code=500, detail="데이터베이스 연결 실패")
        
        # 매출 데이터 조회 로직
        sales_data = self.collection.find_one({"기업명": name}, {"_id": 0, "매출": 1})
        return sales_data.get("매출", []) if sales_data else []
    
    def get_treasure_data(self) -> List[Dict]:
        """투자 보물찾기 데이터 조회"""
        if not self.collection:
            raise HTTPException(status_code=500, detail="데이터베이스 연결 실패")
        
        docs = list(self.collection.find({}, {
            "_id": 0,
            "기업명": 1,
            "업종명": 1,
            "종목코드": 1,
            "짧은요약": 1
        }))
        
        return docs
