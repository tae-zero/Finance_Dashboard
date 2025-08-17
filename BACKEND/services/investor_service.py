# BACKEND/app/services/investor_service.py
from __future__ import annotations

import asyncio
import logging
import warnings
import time
from contextlib import contextmanager
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional

import pandas as pd  # ← 스레드 내부 함수에서도 보이도록 전역 import
from requests.exceptions import JSONDecodeError as ReqJSONDecodeError, RequestException
from pykrx import stock

# noisy 로거/워닝 억제
logging.getLogger("pykrx").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("requests").setLevel(logging.ERROR)
warnings.filterwarnings("ignore")

logger = logging.getLogger("investor_service")


@contextmanager
def _quiet_pykrx(level: int = logging.ERROR):
    """
    pykrx 호출 구간만 조용하게: 잘못된 내부 로깅 포맷으로 터지는
    'Logging error' 스택을 억제하고, 루트 로깅 레벨을 잠시 올린다.
    """
    root = logging.getLogger()
    prev_level = root.level
    prev_raise = getattr(logging, "raiseExceptions", True)
    try:
        root.setLevel(level)
        logging.raiseExceptions = False  # 포맷 에러 traceback 억제
        yield
    finally:
        root.setLevel(prev_level)
        logging.raiseExceptions = prev_raise


def _nearest_business_day_str(yyyymmdd: Optional[str] = None, back_limit: int = 6) -> str:
    """
    최근 영업일을 조용히 탐침. 실패 시 하루씩 후퇴(backoff).
    """
    d = datetime.strptime(yyyymmdd, "%Y%m%d").date() if yyyymmdd else date.today()
    for _ in range(back_limit + 1):
        ds = d.strftime("%Y%m%d")
        try:
            with _quiet_pykrx():
                df = stock.get_market_cap_by_ticker(ds, "KOSPI")  # 위치 인자 사용
            if df is not None and not df.empty:
                return ds
        except Exception:
            pass
        d -= timedelta(days=1)
    # 그래도 못 찾으면 오늘 날짜 반환(후속 단계에서 폴백 처리)
    return date.today().strftime("%Y%m%d")


def _get_market_trading_value_by_investor_safe(
    start: str, end: str, market_or_ticker: str, max_back: int = 6
):
    """
    투자자 매매대금 조회 안전 래퍼.
    - 휴장/주말/네트워크 이슈 시 직전 영업일로 back-off
    - 위치 인자 사용(키워드 market= 금지)
    - 호출 구간 조용히(_quiet_pykrx)
    - detail=False → detail=True 재시도
    - 멀티인덱스 처리 및 컬럼 정규화
    """
    s = datetime.strptime(start, "%Y%m%d").date()
    e = datetime.strptime(end, "%Y%m%d").date()

    for i in range(max_back + 1):
        try:
            # 1) detail=False로 먼저 시도
            with _quiet_pykrx():
                df = stock.get_market_trading_value_by_investor(
                    s.strftime("%Y%m%d"),  # fromdate
                    e.strftime("%Y%m%d"),  # todate
                    market_or_ticker,      # 3번째 위치 인자 (KOSPI/KOSDAQ/ALL 또는 종목코드)
                    detail=False
                )
            
            if df is None or df.empty:
                # 2) detail=True로 재시도
                with _quiet_pykrx():
                    df = stock.get_market_trading_value_by_investor(
                        s.strftime("%Y%m%d"),
                        e.strftime("%Y%m%d"),
                        market_or_ticker,
                        detail=True
                    )
            
            if df is not None and not df.empty:
                # 멀티인덱스 처리 및 컬럼 정규화
                df = _normalize_investor_dataframe(df)
                return df
            raise ValueError("empty dataframe")
            
        except (ReqJSONDecodeError, RequestException, ValueError) as ex:
            logger.warning(
                "pykrx 투자자 데이터 실패(%s~%s,%s) 재시도 %d/%d: %s",
                s, e, market_or_ticker, i + 1, max_back + 1, ex,
            )
        except Exception as ex:
            # 알 수 없는 예외도 동일하게 backoff 처리
            logger.warning(
                "pykrx 투자자 데이터 예외(%s~%s,%s) 재시도 %d/%d: %s",
                s, e, market_or_ticker, i + 1, max_back + 1, ex,
            )
        # 하루씩 후퇴 + 점진적 대기
        s -= timedelta(days=1)
        e -= timedelta(days=1)
        time.sleep(0.6 * (i + 1))
    return None


def _normalize_investor_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    투자자 데이터프레임 정규화:
    - 멀티인덱스 처리
    - 컬럼명 공백 제거, 튜플 평탄화
    - 순매수 > 거래대금 우선 선택
    """
    if df is None or df.empty:
        return df
    
    # 멀티인덱스 처리
    if isinstance(df.columns, pd.MultiIndex):
        # level=1에서 순매수 > 거래대금 우선 선택
        level1_cols = df.columns.get_level_values(1).tolist()
        
        # 순매수 컬럼 우선 선택
        preferred_cols = []
        for col in level1_cols:
            if "순매수" in str(col):
                preferred_cols.append(col)
        
        # 순매수가 없으면 거래대금 컬럼 선택
        if not preferred_cols:
            for col in level1_cols:
                if "거래대금" in str(col):
                    preferred_cols.append(col)
        
        # 선호 컬럼이 있으면 해당 컬럼만 선택
        if preferred_cols:
            selected_cols = []
            for col in preferred_cols:
                for full_col in df.columns:
                    if full_col[1] == col:
                        selected_cols.append(full_col)
            
            if selected_cols:
                df = df[selected_cols]
                # level=1 컬럼명만 사용
                df.columns = [col[1] for col in df.columns]
    
    # 컬럼명 정규화
    normalized_cols = {}
    for col in df.columns:
        col_str = str(col).strip()
        # 공백 제거, 튜플 평탄화
        if "|" in col_str:
            col_str = col_str.split("|")[-1]  # 마지막 부분 사용
        normalized_cols[col] = col_str
    
    df = df.rename(columns=normalized_cols)
    
    # 공백 제거
    df.columns = [str(c).strip() for c in df.columns]
    
    return df


class InvestorService:
    def __init__(self):
        pass

    async def get_kospi_investor_value(self):
        return await self.get_kospi_investor_value_impl()

    async def get_kospi_investor_value_impl(self):
        """
        코스피 투자자별 매매대금/순매수 등(스키마는 pykrx 상황에 따라 일부 변동 가능)
        - 어떤 경우에도 dict 반환(폴백 포함)
        - '거래대금' 컬럼 의존성 제거 (과거 KeyError 원인 제거)
        """
        try:
            def _fetch():
                today = _nearest_business_day_str()
                yesterday = _nearest_business_day_str(
                    (date.today() - timedelta(days=1)).strftime("%Y%m%d")
                )

                df = _get_market_trading_value_by_investor_safe(
                    start=yesterday, end=today, market_or_ticker="KOSPI", max_back=6
                )
                if df is None:
                    logger.warning("pykrx 투자자 데이터 조회 실패: 휴장/네트워크/응답 이상")
                    return {"투자자별_거래량": self._get_static_investor_data()}

                # 대표 컬럼들만 안전하게 추출
                cols = df.columns.tolist()
                pick = {
                    "개인": "individual",
                    "외국인": "foreign",
                    "기관": "institution",
                    "금융투자": "financial",
                    "보험": "insurance",
                    "투신": "investment",
                    "은행": "bank",
                    "연기금": "pension",
                    "기타법인": "other",
                }

                out: List[Dict] = []
                for idx in df.index:
                    row = df.loc[idx]
                    item = {"date": idx.strftime("%Y-%m-%d") if hasattr(idx, "strftime") else str(idx)}
                    for k, newk in pick.items():
                        try:
                            item[newk] = int(row[k]) if k in cols and pd.notna(row[k]) else 0
                        except Exception:
                            item[newk] = 0
                    out.append(item)

                if not out:
                    logger.warning("투자자 데이터 파싱 결과 없음 → 폴백")
                    return {"투자자별_거래량": self._get_static_investor_data()}

                logger.info("pykrx로 투자자 데이터 조회 성공")
                return {"투자자별_거래량": out}

            return await asyncio.to_thread(_fetch)

        except Exception as e:
            logger.error("❌ 투자자 데이터 조회 실패(최상위): %s", e)
            return {"투자자별_거래량": self._get_static_investor_data()}

    def _get_static_investor_data(self):
        today = date.today().strftime("%Y-%m-%d")
        yest = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
        return [
            {
                "date": yest,
                "individual": 1500000000000,
                "foreign": 800000000000,
                "institution": 1200000000000,
                "financial": 300000000000,
                "insurance": 200000000000,
                "investment": 150000000000,
                "bank": 100000000000,
                "pension": 500000000000,
                "other": 250000000000,
            },
            {
                "date": today,
                "individual": 1600000000000,
                "foreign": 850000000000,
                "institution": 1250000000000,
                "financial": 320000000000,
                "insurance": 210000000000,
                "investment": 160000000000,
                "bank": 110000000000,
                "pension": 520000000000,
                "other": 260000000000,
            },
        ]

    async def get_investor_summary(self, ticker: str):
        """
        종목별 최신 투자자 요약 (가능하면 사용, 실패 시 에러 메시지 dict)
        """
        try:
            def _fetch():
                today = _nearest_business_day_str()
                yesterday = _nearest_business_day_str(
                    (date.today() - timedelta(days=1)).strftime("%Y%m%d")
                )

                try:
                    # detail=False로 먼저 시도
                    with _quiet_pykrx():
                        df = stock.get_market_trading_value_by_investor(
                            yesterday, today, ticker, detail=False
                        )
                    
                    if df is None or df.empty:
                        # detail=True로 재시도
                        with _quiet_pykrx():
                            df = stock.get_market_trading_value_by_investor(
                                yesterday, today, ticker, detail=True
                            )
                    
                    if df is None or df.empty:
                        return {"error": "투자자 요약 데이터가 없습니다"}

                    # 데이터프레임 정규화
                    df = _normalize_investor_dataframe(df)
                    
                    latest = df.iloc[-1]
                    res = {
                        "ticker": ticker,
                        "date": latest.name.strftime("%Y-%m-%d") if hasattr(latest.name, "strftime") else str(latest.name),
                        "individual": int(latest["개인"]) if "개인" in latest.index else 0,
                        "foreign": int(latest["외국인"]) if "외국인" in latest.index else 0,
                        "institution": int(latest["기관"]) if "기관" in latest.index else 0,
                    }
                    # 총합(숫자 컬럼만)
                    try:
                        res["total"] = int(pd.to_numeric(latest, errors="coerce").fillna(0).sum())
                    except Exception:
                        res["total"] = 0
                    return res
                except Exception as e:
                    logger.warning("pykrx 개별 종목 데이터 실패(%s): %s", ticker, e)
                    return {"error": f"종목 {ticker} 데이터 조회 실패"}

            return await asyncio.to_thread(_fetch)

        except Exception as e:
            logger.error("❌ 투자자 요약 조회 실패(%s): %s", ticker, e)
            return {"error": str(e)}

    async def get_investor_trends(self, days: int = 30):
        """
        최근 n일 투자자 트렌드. 실패 시 에러 dict.
        """
        try:
            def _fetch():
                end_d = date.today()
                start_d = end_d - timedelta(days=days)
                try:
                    # detail=False로 먼저 시도
                    with _quiet_pykrx():
                        df = stock.get_market_trading_value_by_investor(
                            start_d.strftime("%Y%m%d"),
                            end_d.strftime("%Y%m%d"),
                            "KOSPI",
                            detail=False
                        )
                    
                    if df is None or df.empty:
                        # detail=True로 재시도
                        with _quiet_pykrx():
                            df = stock.get_market_trading_value_by_investor(
                                start_d.strftime("%Y%m%d"),
                                end_d.strftime("%Y%m%d"),
                                "KOSPI",
                                detail=True
                            )
                    
                    if df is None or df.empty:
                        return {"error": "트렌드 데이터가 없습니다"}

                    # 데이터프레임 정규화
                    df = _normalize_investor_dataframe(df)

                    dates = [d.strftime("%Y-%m-%d") if hasattr(d, "strftime") else str(d) for d in df.index]
                    trends = {
                        "individual": df["개인"].tolist() if "개인" in df.columns else [],
                        "foreign": df["외국인"].tolist() if "외국인" in df.columns else [],
                        "institution": df["기관"].tolist() if "기관" in df.columns else [],
                        "dates": dates,
                    }
                    return {"투자자_트렌드": trends}
                except Exception as e:
                    logger.warning("pykrx 트렌드 데이터 실패: %s", e)
                    return {"error": "트렌드 데이터 조회 실패"}

            return await asyncio.to_thread(_fetch)

        except Exception as e:
            logger.error("❌ 투자자 트렌드 조회 실패: %s", e)
            return {"error": str(e)}


# 인스턴스 (라우터에서 import)
investor_service = InvestorService()
