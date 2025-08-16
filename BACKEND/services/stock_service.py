import datetime as dt
import logging
import time
from typing import List, Optional, Dict

from requests.exceptions import JSONDecodeError as ReqJSONDecodeError, RequestException

# 외부 데이터 소스
from pykrx import stock
import FinanceDataReader as fdr
import yfinance as yf


logger = logging.getLogger(__name__)

# ---------- pykrx: 안전 호출 ----------
def _get_index_ohlcv_safe(ticker: str, start: str, end: str):
    """
    pykrx가 간헐적으로 빈 응답/HTML을 주며 JSONDecodeError를 터뜨리는 것을 방어.
    호출 구간만 root 로그 레벨을 WARNING으로 올려 pykrx 내부의 잘못된 logging.info 포맷도 회피.
    """
    root = logging.getLogger()
    prev_level = root.level
    try:
        root.setLevel(logging.WARNING)  # pykrx 내부 잘못된 info 호출 회피
        for i in range(3):
            try:
                df = stock.get_index_ohlcv_by_date(fromdate=start, todate=end, ticker=ticker)
                if df is not None and not df.empty:
                    return df
                raise ValueError("pykrx returned empty DataFrame")
            except (ReqJSONDecodeError, ValueError, RequestException) as e:
                logger.warning("pykrx 실패(%s) - 재시도 %d/3: %s", ticker, i + 1, e)
                time.sleep(0.7 * (i + 1))
        return None
    finally:
        root.setLevel(prev_level)


# ---------- FDR ----------
def _fdr_series(symbol: str, start_date: dt.date, end_date: dt.date) -> Optional[List[Dict]]:
    try:
        df = fdr.DataReader(symbol, start_date, end_date)
        if df is None or df.empty:
            return None
        df = df.reset_index()
        return [
            {"Date": d.strftime("%Y-%m-%d"), "Close": float(c)}
            for d, c in zip(df["Date"], df["Close"])
            if c is not None
        ]
    except Exception as e:
        logger.warning("FDR 실패(%s): %s", symbol, e)
        return None


# ---------- yfinance ----------
def _yf_series(symbol: str, period: str = "1y", interval: str = "1d") -> Optional[List[Dict]]:
    try:
        df = yf.download(
            symbol,
            period=period,
            interval=interval,
            group_by="ticker",
            auto_adjust=False,
            progress=False,
            threads=False,
        )
        if df is None or df.empty:
            return None
        df = df.reset_index()
        out = []
        for d, c in zip(df["Date"], df["Close"]):
            if c is None:
                continue
            d = d.strftime("%Y-%m-%d") if hasattr(d, "strftime") else str(d)
            out.append({"Date": d, "Close": float(c)})
        return out
    except Exception as e:
        logger.warning("yfinance 실패(%s): %s", symbol, e)
        return None


# ---------- 공개 함수 ----------
def get_kospi_series() -> List[Dict]:
    """
    KOSPI 지수 시계열을 리스트[{"Date", "Close"}]로 반환.
    소스 체인: pykrx(1001) → FDR(^KS11) → yfinance(^KS11) → 정적 폴백
    """
    today = dt.date.today()
    start_d = today - dt.timedelta(days=365)

    # pykrx (KOSPI index ticker=1001)
    start = start_d.strftime("%Y%m%d")
    end = today.strftime("%Y%m%d")
    df = _get_index_ohlcv_safe("1001", start, end)
    if df is not None:
        df = df.reset_index()
        return [
            {"Date": d.strftime("%Y-%m-%d"), "Close": float(c)}
            for d, c in zip(df["날짜"], df["종가"])
            if c is not None
        ]

    # FDR
    data = _fdr_series("^KS11", start_d, today)
    if data:
        return data

    # yfinance
    data = _yf_series("^KS11", period="1y", interval="1d")
    if data:
        return data

    # 최후 폴백 (스키마 유지!)
    return [
        {"Date": "2025-07-18", "Close": 2450.0},
        {"Date": "2025-07-19", "Close": 2425.0},
        {"Date": "2025-07-20", "Close": 2575.0},
    ]