import asyncio
import logging
import warnings
import time
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional

from requests.exceptions import JSONDecodeError as ReqJSONDecodeError, RequestException
from pykrx import stock

# noisy 로거/워닝 억제
logging.getLogger("pykrx").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("requests").setLevel(logging.ERROR)
warnings.filterwarnings("ignore")

logger = logging.getLogger("investor_service")


def _nearest_business_day_str(yyyymmdd: Optional[str] = None, back_limit: int = 6) -> str:
    d = datetime.strptime(yyyymmdd, "%Y%m%d").date() if yyyymmdd else date.today()
    for _ in range(back_limit + 1):
        ds = d.strftime("%Y%m%d")
        try:
            df = stock.get_market_cap_by_ticker(ds, "KOSPI")
            if df is not None and not df.empty:
                return ds
        except Exception:
            pass
        d -= timedelta(days=1)
    return date.today().strftime("%Y%m%d")


def _get_market_trading_value_by_investor_safe(
    start: str, end: str, market_or_ticker: str, max_back: int = 6
):
    """
    투자자 매매대금 조회 안전 래퍼.
    - 휴장/주말/네트워크 이슈 시 직전 영업일로 back-off
    - 위치 인자 사용(키워드 market= 금지)
    """
    s = datetime.strptime(start, "%Y%m%d").date()
    e = datetime.strptime(end, "%Y%m%d").date()

    for i in range(max_back + 1):
        try:
            df = stock.get_market_trading_value_by_investor(
                s.strftime("%Y%m%d"),  # fromdate
                e.strftime("%Y%m%d"),  # todate
                market_or_ticker,      # 3번째 위치 인자
                # detail/etf/etn/elw 옵션은 기본값으로 둠
            )
            if df is not None and not df.empty:
                # 컬럼 공백/이상치 정리
                df.columns = [str(c).strip() for c in df.columns]
                return df
            raise ValueError("empty dataframe")
        except (ReqJSONDecodeError, RequestException, ValueError) as ex:
            logger.warning(
                "pykrx 투자자 데이터 실패(%s~%s,%s) 재시도 %d/%d: %s",
                s, e, market_or_ticker, i + 1, max_back + 1, ex,
            )
            s -= timedelta(days=1)
            e -= timedelta(days=1)
            time.sleep(0.6 * (i + 1))
        except Exception as ex:
            # 알 수 없는 예외도 동일하게 backoff 처리
            logger.warning(
                "pykrx 투자자 데이터 예외(%s~%s,%s) 재시도 %d/%d: %s",
                s, e, market_or_ticker, i + 1, max_back + 1, ex,
            )
            s -= timedelta(days=1)
            e -= timedelta(days=1)
            time.sleep(0.6 * (i + 1))
    return None


class InvestorService:
    def __init__(self):
        pass

    async def get_kospi_investor_value(self):
        return await self.get_kospi_investor_value_impl()

    async def get_kospi_investor_value_impl(self):
        """
        코스피 투자자별 매매대금/순매수 등(스키마는 pykrx 상황에 따라 일부 변동 가능)
        - 어떤 경우에도 dict 반환(폴백 포함)
        - '거래대금' 컬럼 의존성 제거 (과거 에러 원인)
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
                    return self._get_static_investor_data()

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
                        item[newk] = int(row[k]) if k in cols and k in row.index and pd.notna(row[k]) else 0
                    out.append(item)

                if not out:
                    logger.warning("투자자 데이터 파싱 결과 없음 → 폴백")
                    return self._get_static_investor_data()

                logger.info("pykrx로 투자자 데이터 조회 성공")
                return {"투자자별_거래량": out}

            import pandas as pd  # 지역 import (pd.notna 사용)
            return await asyncio.to_thread(_fetch)

        except Exception as e:
            logger.error("❌ 투자자 데이터 조회 실패(최상위): %s", e)
            return self._get_static_investor_data()

    def _get_static_investor_data(self):
        today = date.today().strftime("%Y-%m-%d")
        yest = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
        return {
            "투자자별_거래량": [
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
        }

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
                    df = stock.get_market_trading_value_by_investor(
                        yesterday, today, ticker  # 3번째 위치 인자에 종목코드
                    )
                    if df is None or df.empty:
                        return {"error": "투자자 요약 데이터가 없습니다"}

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
                        res["total"] = int(latest.select_dtypes(include=["number"]).sum())
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
                    df = stock.get_market_trading_value_by_investor(
                        start_d.strftime("%Y%m%d"),
                        end_d.strftime("%Y%m%d"),
                        "KOSPI",
                    )
                    if df is None or df.empty:
                        return {"error": "트렌드 데이터가 없습니다"}

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
