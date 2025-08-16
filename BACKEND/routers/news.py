from fastapi import APIRouter, HTTPException, Query
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.news_service import NewsService
from typing import List, Dict
from datetime import datetime
import logging

router = APIRouter(prefix="/news", tags=["뉴스"])
logger = logging.getLogger("news_router")

# 서비스 인스턴스
news_service = NewsService()

@router.get("/hot/kospi")
async def get_kospi_news():
    """코스피 관련 뉴스 조회"""
    try:
        return await news_service.get_kospi_news()
    except (ValueError, RuntimeError) as e:
        logger.warning("외부 데이터 오류: %s", e)
        raise HTTPException(status_code=503, detail="외부 서비스 일시적 오류")
    except Exception as e:
        logger.exception("서버 내부 오류")
        raise HTTPException(status_code=500, detail="내부 서버 오류")

@router.get("/earnings")
async def get_earnings_news():
    """실적 발표 관련 뉴스 조회"""
    try:
        return await news_service.get_earnings_news()
    except (ValueError, RuntimeError) as e:
        logger.warning("외부 데이터 오류: %s", e)
        raise HTTPException(status_code=503, detail="외부 서비스 일시적 오류")
    except Exception as e:
        logger.exception("서버 내부 오류")
        raise HTTPException(status_code=500, detail="내부 서버 오류")

@router.get("/search")
async def search_company_news(keyword: str = Query(..., description="검색 키워드")):
    """기업별 키워드 뉴스 검색"""
    try:
        return await news_service.search_company_news(keyword)
    except (ValueError, RuntimeError) as e:
        logger.warning("외부 데이터 오류: %s", e)
        raise HTTPException(status_code=503, detail="외부 서비스 일시적 오류")
    except Exception as e:
        logger.exception("서버 내부 오류")
        raise HTTPException(status_code=500, detail="내부 서버 오류")

@router.get("/analyst/report")
async def get_analyst_report(code: str = Query(..., description="종목 코드 (예: A005930)")):
    """종목분석 리포트 조회"""
    try:
        return await news_service.get_analyst_reports(code)
    except (ValueError, RuntimeError) as e:
        logger.warning("외부 데이터 오류: %s", e)
        raise HTTPException(status_code=503, detail="외부 서비스 일시적 오류")
    except Exception as e:
        logger.exception("서버 내부 오류")
        raise HTTPException(status_code=500, detail="내부 서버 오류")
