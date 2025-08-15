from fastapi import APIRouter, HTTPException, Query
from services.stock_service import StockService
from typing import List, Dict

router = APIRouter(prefix="/stock", tags=["주가 정보"])

# 서비스 인스턴스
stock_service = StockService()

@router.get("/price/{ticker}")
async def get_stock_price(ticker: str, period: str = Query("3y", description="조회 기간")):
    """주가 데이터 조회"""
    return stock_service.get_stock_price(ticker, period)

@router.get("/kospi/index")
async def get_kospi_data():
    """코스피 지수 데이터 조회"""
    return stock_service.get_kospi_data()

@router.get("/marketcap/top10")
async def get_market_cap_top10():
    """시가총액 TOP10 조회"""
    return stock_service.get_market_cap_top10()

@router.get("/volume/top5")
async def get_top_volume():
    """거래량 TOP5 조회"""
    return stock_service.get_top_volume()

@router.get("/top_volume")
async def get_top_volume_alt():
    """거래량 TOP5 조회 (대체 엔드포인트)"""
    return stock_service.get_top_volume()

@router.get("/industry/{name}")
async def get_industry_analysis(name: str):
    """산업별 재무지표 분석 정보 조회"""
    return stock_service.get_industry_analysis(name)

@router.get("/metrics/{name}")
async def get_company_metrics(name: str):
    """기업 재무지표 JSON 조회"""
    return stock_service.get_company_metrics(name)
