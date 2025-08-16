from fastapi import APIRouter, HTTPException
from typing import Dict, List
import logging
from utils.data_processor import data_processor

logger = logging.getLogger("stock_router")
router = APIRouter(prefix="/api/v1/stock")

@router.get("/price/{ticker}")
async def get_stock_price(ticker: str) -> Dict:
    """주식 가격 데이터 조회"""
    try:
        return await data_processor.get_stock_data(ticker)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"주가 데이터 조회 실패: {str(e)}")
        raise HTTPException(status_code=503, detail=str(e))

@router.get("/kospi/index")
async def get_kospi_index() -> Dict:
    """코스피 지수 데이터 조회"""
    try:
        return await data_processor.get_kospi_data()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"코스피 데이터 조회 실패: {str(e)}")
        raise HTTPException(status_code=503, detail=str(e))

@router.get("/marketcap/top10")
async def get_market_cap_top10() -> List[Dict]:
    """시가총액 상위 10개 기업 조회"""
    try:
        return await data_processor.get_market_cap_data()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"시가총액 데이터 조회 실패: {str(e)}")
        raise HTTPException(status_code=503, detail=str(e))