from fastapi import APIRouter, HTTPException, Query
from services.investor_service import InvestorService
from typing import List, Dict

router = APIRouter(prefix="/investor", tags=["투자자 분석"])

# 서비스 인스턴스
investor_service = InvestorService()

@router.get("/summary/{ticker}")
async def get_investor_summary(ticker: str):
    """기업별 투자자 거래량 분석"""
    return investor_service.get_investor_summary(ticker)

@router.get("/kospi/value")
async def get_kospi_investor_value():
    """코스피 투자자별 매수/매도량 분석"""
    return investor_service.get_kospi_investor_value()

@router.get("/value")
async def get_investor_value():
    """코스피 투자자별 매수/매도량 분석 (메인 엔드포인트)"""
    return investor_service.get_kospi_investor_value()

@router.get("/rankings/top5")
async def get_top_rankings():
    """매출액, DPS, 영업이익률 상위 5개 조회"""
    return investor_service.get_top_rankings()

@router.get("/trends")
async def get_investor_trends(days: int = Query(30, description="분석 기간 (일)")):
    """투자자 트렌드 분석"""
    return investor_service.get_investor_trends(days)
