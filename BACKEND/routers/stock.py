from fastapi import APIRouter, HTTPException
from typing import Dict, List
import logging
from services.stock_service import StockService

logger = logging.getLogger("stock_router")
router = APIRouter(prefix="/stock")

stock_service = StockService()

@router.get("/price/{ticker}")
async def get_stock_price(ticker: str) -> Dict:
    """주식 가격 데이터 조회"""
    try:
        data = await stock_service.get_stock_price(ticker)
        return {"data": data}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"주가 데이터 조회 실패: {str(e)}")
        raise HTTPException(status_code=503, detail=str(e))

@router.get("/kospi/index")
async def get_kospi_index() -> Dict:
    """코스피 지수 데이터 조회"""
    try:
        data = await stock_service.get_kospi_data()
        return {"data": data}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"코스피 데이터 조회 실패: {str(e)}")
        raise HTTPException(status_code=503, detail=str(e))

@router.get("/marketcap/top10")
async def get_market_cap_top10() -> Dict:
    """시가총액 상위 10개 기업 조회"""
    try:
        data = await stock_service.get_market_cap_top10()
        return {"data": data}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"시가총액 데이터 조회 실패: {str(e)}")
        raise HTTPException(status_code=503, detail=str(e))

@router.get("/volume/top5")
async def get_top_volume() -> Dict:
    """거래량 상위 5개 기업 조회"""
    try:
        data = await stock_service.get_top_volume()
        return {"data": data}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"거래량 데이터 조회 실패: {str(e)}")
        raise HTTPException(status_code=503, detail=str(e))

@router.get("/industry/{name}")
async def get_industry_analysis(name: str) -> Dict:
    """산업별 분석 데이터 조회"""
    try:
        data = await stock_service.get_industry_analysis(name)
        return {"data": data}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"산업 분석 데이터 조회 실패: {str(e)}")
        raise HTTPException(status_code=503, detail=str(e))