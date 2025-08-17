from fastapi import APIRouter, HTTPException, Query
import sys
import os
import json

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.company_service import CompanyService
from typing import List, Dict

router = APIRouter(prefix="/company", tags=["기업 정보"])

# 서비스 인스턴스
company_service = CompanyService()

@router.get("/{name}")
async def get_company_data(name: str):
    """기업 상세 정보 조회"""
    return await company_service.get_company_data(name)

@router.get("/names/all")
async def get_all_company_names():
    """전체 기업명 목록 조회"""
    return await company_service.get_all_company_names()

@router.get("/metrics/{name}")
async def get_company_metrics(name: str):
    """기업 재무지표 조회"""
    return await company_service.get_company_metrics(name)

@router.get("/sales/{name}")
async def get_company_sales(name: str):
    """기업 매출 데이터 조회"""
    return await company_service.get_sales_data(name)

@router.get("/treasure/data")
async def get_treasure_data():
    """투자 보물찾기 데이터 조회"""
    return await company_service.get_treasure_data()

@router.get("/data/financial-metrics")
async def get_financial_metrics():
    """기업별 재무지표 JSON 데이터"""
    try:
        with open("기업별_재무지표.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="재무지표 파일을 찾을 수 없습니다")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"재무지표 데이터 로드 실패: {str(e)}")

@router.get("/data/industry-metrics")
async def get_industry_metrics():
    """산업별 지표 JSON 데이터"""
    try:
        with open("industry_metrics.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="산업지표 파일을 찾을 수 없습니다")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"산업지표 데이터 로드 실패: {str(e)}")

@router.get("/data/sales-data")
async def get_sales_data():
    """매출비중 차트 데이터 JSON"""
    try:
        with open("매출비중_chartjs_데이터.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="매출데이터 파일을 찾을 수 없습니다")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"매출데이터 로드 실패: {str(e)}")

@router.get("/data/shareholder-data")
async def get_shareholder_data():
    """지분현황 JSON 데이터"""
    try:
        with open("지분현황.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="지분현황 파일을 찾을 수 없습니다")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"지분현황 데이터 로드 실패: {str(e)}")
