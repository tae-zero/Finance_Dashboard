import os
from fastapi import HTTPException
from utils.database import db_manager
import logging
from bson import ObjectId
from typing import Dict

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

    def get_company_data(self, company_name: str) -> Dict:
        """기업 데이터 조회"""
        try:
            logger.info(f"🔍 기업 검색 시작: '{company_name}'")
            
            # 컬렉션 가져오기
            collection = self._get_collection("explain")
            logger.info(f"📊 컬렉션명: explain")
            
            # 기업명으로 검색
            query = {"기업명": company_name}
            logger.info(f"🔍 검색 쿼리: {query}")
            
            # 전체 문서 수 확인
            total_count = collection.count_documents({})
            logger.info(f"📈 컬렉션 총 문서 수: {total_count}")
            
            # 첫 번째 문서의 구조 확인
            first_doc = collection.find_one({})
            if first_doc:
                logger.info(f"📋 첫 번째 문서 키들: {list(first_doc.keys())}")
                if '기업명' in first_doc:
                    logger.info(f"📋 '기업명' 필드 값: '{first_doc['기업명']}'")
            
            # 실제 검색 실행
            company = collection.find_one(query)
            
            if company:
                logger.info(f"✅ 기업 데이터 찾음: {company_name}")
                
                # 실제 데이터 구조 로깅
                logger.info(f"📋 찾은 기업 데이터 키들: {list(company.keys())}")
                
                # 요약 관련 필드 확인
                summary_fields = [key for key in company.keys() if '요약' in key or '개요' in key]
                logger.info(f"📋 요약/개요 관련 필드들: {summary_fields}")
                
                for field in summary_fields:
                    value = company.get(field, '')
                    logger.info(f"📋 '{field}' 필드 값: '{str(value)[:100]}...'")
                
                # ObjectId 변환
                company = self._convert_objectid(company)
                return company
            else:
                logger.warning(f"⚠️ 기업을 찾을 수 없음: {company_name}")
                
                # 유사한 기업명 찾기
                similar_companies = collection.find({"기업명": {"$regex": company_name[:2]}}).limit(5)
                similar_names = [doc.get('기업명', '') for doc in similar_companies]
                logger.info(f"🔍 유사한 기업명들: {similar_names}")
                
                return None
                
        except Exception as e:
            logger.error(f"❌ 기업 데이터 조회 실패 ({company_name}): {e}")
            return None

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