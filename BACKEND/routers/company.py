from fastapi import APIRouter, HTTPException, Query
import sys
import os

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
