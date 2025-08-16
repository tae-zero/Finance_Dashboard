import os
from fastapi import HTTPException
from utils.database import db_manager
import logging

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

    async def get_company_data(self, company_name: str):
        """기업 데이터 조회"""
        try:
            collection = self._get_collection(os.getenv("COLLECTION_USERS", "users"))
            company_data = collection.find_one({"name": company_name})
            if not company_data:
                raise HTTPException(status_code=404, detail=f"기업을 찾을 수 없습니다: {company_name}")
            return company_data
        except Exception as e:
            logger.error(f"기업 데이터 조회 실패 ({company_name}): {str(e)}")
            raise HTTPException(status_code=503, detail="기업 데이터 조회 실패")

    async def get_all_company_names(self):
        """모든 기업 이름 조회"""
        try:
            collection = self._get_collection(os.getenv("COLLECTION_USERS", "users"))
            companies = collection.find({}, {"name": 1})
            company_names = []
            for company in companies:
                if "name" in company and company["name"]:
                    company_names.append(company["name"])
            return company_names
        except Exception as e:
            logger.error(f"기업 목록 조회 실패: {str(e)}")
            raise HTTPException(status_code=503, detail="기업 목록 조회 실패")

    async def get_company_metrics(self, company_name: str):
        """기업 지표 조회"""
        try:
            collection = self._get_collection(os.getenv("COLLECTION_USERS", "users"))
            metrics = collection.find_one(
                {"name": company_name},
                {"metrics": 1}
            )
            if not metrics:
                raise HTTPException(status_code=404, detail=f"기업 지표를 찾을 수 없습니다: {company_name}")
            return metrics.get("metrics", {})
        except Exception as e:
            logger.error(f"기업 지표 조회 실패 ({company_name}): {str(e)}")
            raise HTTPException(status_code=503, detail="기업 지표 조회 실패")

    async def get_sales_data(self, company_name: str):
        """매출 데이터 조회"""
        try:
            collection = self._get_collection(os.getenv("COLLECTION_USERS", "users"))
            sales_data = collection.find_one(
                {"name": company_name},
                {"sales": 1}
            )
            if not sales_data:
                raise HTTPException(status_code=404, detail=f"매출 데이터를 찾을 수 없습니다: {company_name}")
            return sales_data.get("sales", {})
        except Exception as e:
            logger.error(f"매출 데이터 조회 실패 ({company_name}): {str(e)}")
            raise HTTPException(status_code=503, detail="매출 데이터 조회 실패")

    async def get_treasure_data(self):
        """보물찾기 데이터 조회"""
        try:
            collection = self._get_collection(os.getenv("COLLECTION_USERS", "users"))
            treasure_data = collection.find({}, {"name": 1, "treasure": 1})
            return list(treasure_data)
        except Exception as e:
            logger.error(f"보물찾기 데이터 조회 실패: {str(e)}")
            raise HTTPException(status_code=503, detail="보물찾기 데이터 조회 실패")

# 서비스 인스턴스 생성
company_service = CompanyService()