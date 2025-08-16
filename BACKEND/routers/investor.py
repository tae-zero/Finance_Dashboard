from fastapi import APIRouter, HTTPException, Query
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.investor_service import InvestorService
from typing import List, Dict
from datetime import datetime
import logging

logger = logging.getLogger("investor_router")
router = APIRouter(prefix="/investor", tags=["투자자 분석"])

# 서비스 인스턴스
investor_service = InvestorService()

@router.get("/summary/{ticker}")
async def get_investor_summary(ticker: str):
    """기업별 투자자 거래량 분석"""
    try:
        return await investor_service.get_investor_summary(ticker)
    except (ValueError, RuntimeError) as e:
        logger.warning("외부 데이터 오류: %s", e)
        raise HTTPException(status_code=503, detail="외부 서비스 일시적 오류")
    except Exception as e:
        logger.exception("서버 내부 오류")
        raise HTTPException(status_code=500, detail="내부 서버 오류")

@router.get("/kospi/value")
async def get_kospi_investor_value():
    """코스피 투자자별 매수/매도량 분석"""
    try:
        return await investor_service.get_kospi_investor_value()
    except (ValueError, RuntimeError) as e:
        logger.warning("외부 데이터 오류: %s", e)
        raise HTTPException(status_code=503, detail="외부 서비스 일시적 오류")
    except Exception as e:
        logger.exception("서버 내부 오류")
        raise HTTPException(status_code=500, detail="내부 서버 오류")

@router.get("/value")
async def get_investor_value():
    """코스피 투자자별 매수/매도량 분석 (메인 엔드포인트)"""
    try:
        return await investor_service.get_kospi_investor_value()
    except (ValueError, RuntimeError) as e:
        logger.warning("외부 데이터 오류: %s", e)
        raise HTTPException(status_code=503, detail="외부 서비스 일시적 오류")
    except Exception as e:
        logger.exception("서버 내부 오류")
        raise HTTPException(status_code=500, detail="내부 서버 오류")

@router.get("/rankings/top5")
async def get_top_rankings():
    """매출액, DPS, 영업이익률 상위 5개 조회"""
    try:
        return await investor_service.get_top_rankings()
    except (ValueError, RuntimeError) as e:
        logger.warning("외부 데이터 오류: %s", e)
        raise HTTPException(status_code=503, detail="외부 서비스 일시적 오류")
    except Exception as e:
        logger.exception("서버 내부 오류")
        raise HTTPException(status_code=500, detail="내부 서버 오류")

@router.get("/trends")
async def get_investor_trends(days: int = Query(30, description="분석 기간 (일)")):
    """투자자 트렌드 분석"""
    try:
        return await investor_service.get_investor_trends(days)
    except (ValueError, RuntimeError) as e:
        logger.warning("외부 데이터 오류: %s", e)
        raise HTTPException(status_code=503, detail="외부 서비스 일시적 오류")
    except Exception as e:
        logger.exception("서버 내부 오류")
        raise HTTPException(status_code=500, detail="내부 서버 오류")
