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
        """기업 데이터 조회 (explain 컬렉션에서 짧은요약, users에서 재무지표)"""
        try:
            logger.info(f"🔍 기업 검색 시작: '{company_name}'")
            
            # 1) explain 컬렉션에서 짧은요약 가져오기
            explain_collection = self._get_collection("explain")
            logger.info(f"📊 explain 컬렉션에서 짧은요약 조회")
            
            explain_query = {"기업명": company_name}
            explain_data = explain_collection.find_one(explain_query)
            
            # 2) users 컬렉션에서 재무지표 가져오기
            users_collection = self._get_collection("users")
            logger.info(f"📊 users 컬렉션에서 재무지표 조회")
            
            users_query = {"기업명": company_name}
            users_data = users_collection.find_one(users_query)
            
            # 3) 데이터 병합
            if explain_data or users_data:
                logger.info(f"✅ 기업 데이터 찾음: {company_name}")
                
                # 기본 데이터 구조 생성
                company = {}
                
                # explain에서 짧은요약 추가
                if explain_data:
                    company.update({
                        "기업명": explain_data.get("기업명"),
                        "종목코드": explain_data.get("종목코드"),
                        "업종명": explain_data.get("업종명"),
                        "짧은요약": explain_data.get("짧은요약")
                    })
                
                # users에서 재무지표 추가
                if users_data:
                    company.update({
                        "지표": users_data.get("지표", {})
                    })
                
                # outline 컬렉션에서 기업개요 가져오기
                try:
                    outline_collection = self._get_collection("outline")
                    outline_query = {"종목": str(company.get("종목코드", ""))}
                    outline_data = outline_collection.find_one(outline_query)
                    
                    if outline_data:
                        company.update({
                            "개요": {
                                "주소": outline_data.get("주", ""),
                                "설립일": outline_data.get("설립일", ""),
                                "대표자": outline_data.get("대표자", ""),
                                "전화번호": outline_data.get("전화번호", ""),
                                "홈페이지": outline_data.get("홈페이지", "")
                            }
                        })
                except Exception as e:
                    logger.warning(f"outline 컬렉션 조회 실패: {e}")
                    company.update({"개요": {}})
                
                # ObjectId 변환
                company = self._convert_objectid(company)
                
                # 지분현황.json에서 해당 기업의 지분 정보 찾기
                try:
                    import json
                    with open("지분현황.json", "r", encoding="utf-8") as f:
                        shareholder_data = json.load(f)
                    
                    # 종목코드로 지분 정보 찾기 (A005930 형태)
                    종목코드_str = str(company.get("종목코드", ""))
                    if 종목코드_str:
                        # 종목코드가 5자리면 앞에 A 추가
                        if len(종목코드_str) == 5:
                            종목코드_key = f"A{종목코드_str}"
                        else:
                            종목코드_key = 종목코드_str
                        
                        if 종목코드_key in shareholder_data:
                            company["지분정보"] = shareholder_data[종목코드_key]
                            logger.info(f"✅ 지분 정보 로드 성공: {종목코드_key}")
                        else:
                            logger.warning(f"⚠️ 지분 정보 없음: {종목코드_key}")
                            company["지분정보"] = []
                    else:
                        company["지분정보"] = []
                        
                except Exception as e:
                    logger.warning(f"지분현황.json 로드 실패: {e}")
                    company["지분정보"] = []
                
                return company
            else:
                logger.warning(f"⚠️ 기업을 찾을 수 없음: {company_name}")
                return None
                
        except Exception as e:
            logger.error(f"❌ 기업 데이터 조회 실패 ({company_name}): {e}")
            return None

    def get_company_financial_metrics(self, company_name: str) -> Dict:
        """기업 재무지표 조회 (users 컬렉션에서)"""
        try:
            collection = self._get_collection("users")
            query = {"기업명": company_name}
            
            company = collection.find_one(query)
            if company:
                # ObjectId 변환
                company = self._convert_objectid(company)
                return company
            else:
                return {"error": "해당 기업의 재무지표를 찾을 수 없습니다."}
                
        except Exception as e:
            logger.error(f"❌ 재무지표 조회 실패 ({company_name}): {e}")
            return {"error": f"재무지표 조회 중 오류 발생: {e}"}

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