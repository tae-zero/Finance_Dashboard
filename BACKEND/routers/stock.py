# BACKEND/app/routers/stock.py
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Path, Query
from typing import Any, Dict
import logging
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.stock_service import StockService

# -------------------------
# 로거
# -------------------------
logger = logging.getLogger("stock_router")

# -------------------------
# 라우터 & 서비스
# -------------------------
router = APIRouter(prefix="/stock", tags=["stock"])
stock_service = StockService()

# 공통 래퍼 (항상 dict로 감싸서 반환)
def _ok(data: Any) -> Dict[str, Any]:
    return {"data": data}

# -------------------------
# 엔드포인트
# -------------------------
@router.get(
    "/price/{ticker}",
    response_model=Dict[str, Any],
    summary="주식 가격 데이터 조회",
)
async def get_stock_price(
    ticker: str = Path(..., description="KRX 종목코드(6자리) 또는 야후티커(예: 005930.KS)")
) -> Dict[str, Any]:
    """
    개별 종목의 시계열/가격 데이터를 조회합니다.
    항상 {"data": ...} 형태로 응답합니다.
    """
    try:
        data = await stock_service.get_stock_price(ticker)
        return _ok(data)
    except HTTPException:
        raise
    except Exception as e:
        # 단일 라인 로그 (레이트리밋/중복로그 방지)
        logger.error("주가 데이터 조회 실패(ticker=%s): %s", ticker, str(e))
        raise HTTPException(status_code=503, detail="stock price service unavailable")


@router.get(
    "/kospi/index",
    response_model=Dict[str, Any],
    summary="코스피 지수 데이터 조회",
)
async def get_kospi_index() -> Dict[str, Any]:
    """
    코스피 지수(^KS11 / KRX 1001 등) 시계열 데이터를 조회합니다.
    소스 체인(pykrx → FDR → yfinance → 정적 폴백)은 서비스 레이어에서 처리.
    """
    try:
        data = await stock_service.get_kospi_data()
        return _ok(data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("코스피 데이터 조회 실패: %s", str(e))
        raise HTTPException(status_code=503, detail="kospi index service unavailable")


@router.get(
    "/marketcap/top10",
    response_model=Dict[str, Any],
    summary="시가총액 상위 10개 기업 조회",
)
async def get_market_cap_top10() -> Dict[str, Any]:
    """
    시가총액 상위 10개 기업 목록을 반환합니다.
    """
    try:
        data = await stock_service.get_market_cap_top10()
        return _ok(data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("시가총액 데이터 조회 실패: %s", str(e))
        raise HTTPException(status_code=503, detail="marketcap service unavailable")


@router.get(
    "/volume/top5",
    response_model=Dict[str, Any],
    summary="거래량 상위 5개 기업 조회",
)
async def get_top_volume() -> Dict[str, Any]:
    """
    거래량 상위 5개 기업 목록을 반환합니다.
    """
    try:
        data = await stock_service.get_top_volume()
        return _ok(data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("거래량 데이터 조회 실패: %s", str(e))
        raise HTTPException(status_code=503, detail="volume service unavailable")


@router.get(
    "/industry/{name}",
    response_model=Dict[str, Any],
    summary="산업별 분석 데이터 조회",
)
async def get_industry_analysis(
    name: str = Path(..., description="산업(업종) 명칭"),
    limit: int = Query(50, ge=1, le=500, description="최대 반환 개수(옵션)")
) -> Dict[str, Any]:
    """
    특정 산업(업종)의 분석 데이터를 조회합니다.
    필요 시 limit 같은 파라미터를 서비스 레이어로 전달하세요.
    """
    try:
        data = await stock_service.get_industry_analysis(name=name, limit=limit)
        return _ok(data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("산업 분석 데이터 조회 실패(name=%s): %s", name, str(e))
        raise HTTPException(status_code=503, detail="industry analysis service unavailable")
