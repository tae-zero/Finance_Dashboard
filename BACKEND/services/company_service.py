from utils.database import db_manager
from utils.data_processor import DataProcessor
from fastapi import HTTPException
from typing import Dict, List, Optional

class CompanyService:
    def __init__(self):
        self.collection = db_manager.collection
        self.explain = db_manager.explain
        self.outline = db_manager.outline
    
    def get_company_data(self, name: str) -> Dict:
        """기업 상세 정보 조회"""
        # 기본 정보 조회
        base = self.collection.find_one({"기업명": name}, {"_id": 0})
        if not base:
            raise HTTPException(status_code=404, detail="기업을 찾을 수 없습니다.")
        
        # 짧은 요약 정보 추가
        explain_doc = self.explain.find_one({"기업명": name}, {"_id": 0, "짧은요약": 1})
        if explain_doc:
            base["짧은요약"] = explain_doc.get("짧은요약")
        
        # 기업 개요 정보 추가
        code = base.get("종목코드")
        if code:
            outline_doc = self.outline.find_one({"종목코드": code}, {"_id": 0})
            if outline_doc:
                base["개요"] = outline_doc
        
        return base
    
    def get_all_company_names(self) -> List[str]:
        """전체 기업명 목록 조회"""
        cursor = self.collection.find({}, {"_id": 0, "기업명": 1})
        names = [doc["기업명"] for doc in cursor if "기업명" in doc]
        
        if not names:
            raise HTTPException(status_code=404, detail="기업명이 없습니다.")
        
        return names
    
    def get_company_metrics(self, name: str) -> Dict:
        """기업 재무지표 조회"""
        # MongoDB에서 기업 지표 조회
        company_data = self.collection.find_one({"기업명": name}, {"_id": 0, "지표": 1})
        
        if not company_data:
            raise HTTPException(status_code=404, detail="해당 기업 지표가 없습니다.")
        
        # 실제 데이터 구조 확인을 위한 로그
        print(f"🔍 {name} 기업 지표 데이터 구조:", company_data.get("지표", {}))
        
        return company_data.get("지표", {})
    
    def get_sales_data(self, name: str) -> List[Dict]:
        """기업 매출 데이터 조회 (CSV 파일 기반)"""
        import pandas as pd
        
        try:
            # CSV 파일 읽기 (경로는 환경변수로 관리하는 것이 좋습니다)
            df = pd.read_csv("NICE_내수수출_코스피.csv")
            
            # 그룹화 및 필터링
            grouped = df.groupby(['종목명', '사업부문', '매출품목명', '구분'])[
                ['2022_12 매출액', '2023_12 매출액', '2024_12 매출액']
            ].sum()
            
            if name not in grouped.index.get_level_values(0):
                raise HTTPException(status_code=404, detail="해당 기업이 없습니다.")
            
            filtered = grouped.loc[name].reset_index()
            return filtered.to_dict(orient="records")
            
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="매출 데이터 파일을 찾을 수 없습니다.")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"매출 데이터 조회 중 오류: {str(e)}")
    
    def get_treasure_data(self) -> List[Dict]:
        """투자 보물찾기 데이터 조회"""
        docs = list(self.collection.find({}, {
            "_id": 0,
            "기업명": 1,
            "업종명": 1,
            "지표": 1
        }))
        
        years = ["2022", "2023", "2024"]
        result = []
        
        for doc in docs:
            기업명 = doc.get("기업명", "알 수 없음")
            업종명 = doc.get("업종명", "알 수 없음")
            지표 = doc.get("지표", {})
            
            try:
                # 각 연도별 지표 추출
                per = {year: 지표.get(f"{year}/12_PER") for year in years}
                pbr = {year: 지표.get(f"{year}/12_PBR") for year in years}
                roe = {year: 지표.get(f"{year}/12_ROE") for year in years}
                mktcap = {year: 지표.get(f"{year}/12_시가총액") for year in years}
                equity = {year: 지표.get(f"{year}/12_지배주주지분") for year in years}
                owner_income = {year: 지표.get(f"{year}/12_지배주주순이익") for year in years}
                
                result.append({
                    "기업명": 기업명,
                    "업종명": 업종명,
                    "PER": per,
                    "PBR": pbr,
                    "ROE": roe,
                    "시가총액": mktcap,
                    "지배주주지분": equity,
                    "지배주주순이익": owner_income
                })
                
            except Exception as e:
                print(f"❌ {기업명} 처리 중 오류: {e}")
                continue
        
        return result
