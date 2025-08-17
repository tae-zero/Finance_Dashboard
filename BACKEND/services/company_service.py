import os
from fastapi import HTTPException
from utils.database import db_manager
import logging
from bson import ObjectId

logger = logging.getLogger("company_service")

class CompanyService:
    def __init__(self):
        # 초기화 시점에 컬렉션을 가져오지 않음
        pass

    def _get_collection(self, collection_name: str):
        """컬렉션 가져오기 (필요할 때마다)"""
        try:
            return db_manager.get_collection(collection_name)
        except Exception as e:
            logger.error(f"컬렉션 가져오기 실패 ({collection_name}): {str(e)}")
            raise HTTPException(status_code=503, detail="데이터베이스 연결 실패")

    def _convert_objectid(self, obj):
        """MongoDB ObjectId를 JSON 직렬화 가능한 형태로 변환"""
        if isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, dict):
            return {k: self._convert_objectid(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_objectid(item) for item in obj]
        else:
            return obj

    async def get_company_data(self, company_name: str):
        """기업 데이터 조회"""
        try:
            collection = self._get_collection(os.getenv("COLLECTION_USERS", "users"))
            company_data = collection.find_one({"기업명": company_name})
            if not company_data:
                raise HTTPException(status_code=404, detail=f"기업을 찾을 수 없습니다: {company_name}")
            
            # ObjectId를 문자열로 변환
            company_data = self._convert_objectid(company_data)
            return company_data
        except Exception as e:
            logger.error(f"기업 데이터 조회 실패 ({company_name}): {str(e)}")
            raise HTTPException(status_code=503, detail="기업 데이터 조회 실패")

    async def get_all_company_names(self):
        """모든 기업 이름 조회"""
        try:
            collection = self._get_collection(os.getenv("COLLECTION_USERS", "users"))
            companies = collection.find({}, {"기업명": 1})
            company_names = []
            for company in companies:
                if "기업명" in company and company["기업명"]:
                    company_names.append(company["기업명"])
            return company_names
        except Exception as e:
            logger.error(f"기업 목록 조회 실패: {str(e)}")
            raise HTTPException(status_code=503, detail="기업 목록 조회 실패")

    async def get_company_metrics(self, company_name: str):
        """기업 지표 조회"""
        try:
            collection = self._get_collection(os.getenv("COLLECTION_USERS", "users"))
            metrics = collection.find_one(
                {"기업명": company_name},
                {"metrics": 1}
            )
            if not metrics:
                raise HTTPException(status_code=404, detail=f"기업 지표를 찾을 수 없습니다: {company_name}")
            
            # ObjectId를 문자열로 변환
            metrics = self._convert_objectid(metrics)
            return metrics.get("metrics", {})
        except Exception as e:
            logger.error(f"기업 지표 조회 실패 ({company_name}): {str(e)}")
            raise HTTPException(status_code=503, detail="기업 지표 조회 실패")

    async def get_sales_data(self, company_name: str):
        """매출 데이터 조회"""
        try:
            collection = self._get_collection(os.getenv("COLLECTION_USERS", "users"))
            sales_data = collection.find_one(
                {"기업명": company_name},
                {"sales": 1}
            )
            if not sales_data:
                raise HTTPException(status_code=404, detail=f"매출 데이터를 찾을 수 없습니다: {company_name}")
            
            # ObjectId를 문자열로 변환
            sales_data = self._convert_objectid(sales_data)
            return sales_data.get("sales", {})
        except Exception as e:
            logger.error(f"매출 데이터 조회 실패 ({company_name}): {str(e)}")
            raise HTTPException(status_code=503, detail="매출 데이터 조회 실패")

    async def get_treasure_data(self):
        """보물찾기 데이터 조회"""
        try:
            collection = self._get_collection(os.getenv("COLLECTION_USERS", "users"))
            treasure_data = collection.find({}, {"기업명": 1, "treasure": 1})
            
            # ObjectId를 문자열로 변환
            treasure_list = []
            for item in treasure_data:
                treasure_list.append(self._convert_objectid(item))
            
            return treasure_list
        except Exception as e:
            logger.error(f"보물찾기 데이터 조회 실패: {str(e)}")
            raise HTTPException(status_code=503, detail="보물찾기 데이터 조회 실패")

# 서비스 인스턴스 생성
company_service = CompanyService()