from fastapi import APIRouter, Request, HTTPException, Query
from services.news_service import NewsService
from typing import List, Dict

router = APIRouter(prefix="/news", tags=["뉴스"])

# 서비스 인스턴스
news_service = NewsService()

@router.get("/hot/kospi")
async def get_kospi_news():
    """코스피 관련 뉴스 조회"""
    return news_service.get_kospi_news()

@router.get("/earnings")
async def get_earnings_news():
    """실적 발표 관련 뉴스 조회"""
    return news_service.get_earnings_news()

@router.get("/search")
async def search_company_news(keyword: str = Query(..., description="검색 키워드")):
    """기업별 키워드 뉴스 검색"""
    return news_service.search_company_news(keyword)

@router.get("/analyst/report")
async def get_analyst_report(code: str = Query(..., description="종목 코드 (예: A005930)")):
    """종목분석 리포트 조회"""
    return news_service.get_analyst_reports(code)
