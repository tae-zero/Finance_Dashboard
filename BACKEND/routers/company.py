from fastapi import APIRouter, HTTPException, Query
import sys
import os
import json

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.company_service import CompanyService
from typing import List, Dict
from fastapi.responses import JSONResponse
import os
from selenium_utils import SeleniumManager

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

@router.get("/company/{company_name}")
async def get_company_data(company_name: str):
    try:
        company_data = company_service.get_company_data(company_name)
        if not company_data:
            raise HTTPException(status_code=404, detail="기업을 찾을 수 없습니다")
        return company_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"기업 데이터 조회 실패: {str(e)}")

@router.get("/company/{company_name}/news")
async def get_company_news(company_name: str):
    """기업별 관련 뉴스 크롤링"""
    try:
        # Selenium을 사용하여 기업별 뉴스 크롤링
        selenium_manager = SeleniumManager()
        
        # 네이버 뉴스에서 기업명으로 검색
        search_query = f"{company_name} 뉴스"
        news_data = selenium_manager.crawl_company_news(search_query, max_news=10)
        
        return {"news": news_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"뉴스 크롤링 실패: {str(e)}")

@router.get("/company/{company_name}/analyst-report")
async def get_company_analyst_report(company_name: str):
    """기업별 애널리스트 리포트 크롤링"""
    try:
        # Selenium을 사용하여 기업별 애널리스트 리포트 크롤링
        selenium_manager = SeleniumManager()
        
        # 한국투자증권 등에서 기업명으로 리포트 검색
        search_query = f"{company_name} 애널리스트 리포트"
        report_data = selenium_manager.crawl_analyst_reports(search_query, max_reports=5)
        
        return {"reports": report_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"애널리스트 리포트 크롤링 실패: {str(e)}")
