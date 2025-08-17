import logging
from datetime import datetime, timedelta, date
from typing import List, Dict, Optional

import yfinance as yf
from pykrx import stock

logger = logging.getLogger("stock_service")


def _to_datestring(d) -> str:
    return d.strftime("%Y-%m-%d") if hasattr(d, "strftime") else str(d)


def _normalize_yf_close(df) -> Optional[List[Dict]]:
    """
    yfinance가 멀티인덱스 컬럼을 줄 때도 Close를 안전하게 뽑아 JSON-friendly로 변환
    """
    if df is None or df.empty:
        return None

    # Close 컬럼 찾기 (단일/멀티인덱스 모두 대응)
    close_col = None
    for col in df.columns:
        if (isinstance(col, tuple) and "Close" in col) or (col == "Close"):
            close_col = col
            break

    if close_col is None:
        logger.warning("yfinance Close 컬럼 없음: %s", list(df.columns))
        return None

    df = df[[close_col]].reset_index()
    df.columns = ["Date", "Close"]
    out = []
    for d, c in zip(df["Date"], df["Close"]):
        if c is None:
            continue
        out.append({"Date": _to_datestring(d), "Close": float(c)})
    return out if out else None


def _nearest_business_day_str(yyyymmdd: Optional[str] = None, back_limit: int = 6) -> str:
    """
    오늘이 휴장/주말일 경우, 최대 back_limit일까지 과거로 보정하여
    KRX가 응답을 주는 최근 영업일 YYYYMMDD 문자열을 반환
    """
    if yyyymmdd:
        d = datetime.strptime(yyyymmdd, "%Y%m%d").date()
    else:
        d = date.today()

    for i in range(back_limit + 1):
        ds = d.strftime("%Y%m%d")
        try:
            # 시가총액 같은 가벼운 엔드포인트로 탐침
            df = stock.get_market_cap_by_ticker(ds, "KOSPI")
            if df is not None and not df.empty:
                return ds
        except Exception:
            pass
        d = d - timedelta(days=1)
    # 그래도 실패하면 오늘 날짜 문자열 반환(어차피 이후 단계에서 폴백)
    return date.today().strftime("%Y%m%d")


class StockService:
    def __init__(self):
        pass

    # 항상 List[Dict] 반환 (빈 경우도 [])
    def get_stock_price(self, ticker: str, period: str = "3y") -> List[Dict]:
        """
        개별 종목 가격. 실패/빈결과여도 [] 반환(예외/에러 dict 금지).
        """
        try:
            # API 요청 제한 방지를 위한 대기
            time.sleep(1)
            
            # period 대신 start/end 사용 (더 안정적)
            today = date.today()
            start = today - timedelta(days=365)
            end = today + timedelta(days=1)
            
            df = yf.download(ticker, start=start, end=end, interval="1d", progress=False, threads=False)
            data = _normalize_yf_close(df)
            if data is None:
                logger.warning("yfinance 종목 데이터 없음: %s", ticker)
                return []
            return data
        except Exception as e:
            logger.warning("yfinance 종목 조회 실패(%s): %s", ticker, e)
            return []

    def get_kospi_data(self) -> List[Dict]:
        """
        코스피 지수 데이터: FDR(KS11) → yfinance(^KS11) → 정적 폴백
        어떤 경우에도 예외를 올리지 않고 리스트 반환.
        """
        try:
            today = date.today()
            start = today - timedelta(days=365)
            end = today + timedelta(days=1)  # 서버 타임존 차이로 하루 여유

            # 1) FinanceDataReader (가장 안정적) - 1회만 시도 후 429면 즉시 폴백
            try:
                time.sleep(1)  # API 요청 제한 방지
                import FinanceDataReader as fdr
                df = fdr.DataReader("KS11", start, end)
                if df is not None and not df.empty:
                    df = df.reset_index()
                    out = []
                    for d, c in zip(df["Date"], df["Close"]):
                        if c is None:
                            continue
                        out.append({"Date": _to_datestring(d), "Close": float(c)})
                    if out:
                        logger.info("FDR(KS11)로 코스피 데이터 조회 성공")
                        return out
                logger.warning("FDR로 코스피 데이터가 비어있습니다")
            except Exception as e:
                # 429 등 FDR 오류 시 즉시 yfinance로 폴백 (재시도 안함)
                logger.warning("FDR 실패(KS11) - yfinance로 폴백: %s", e)

            # 2) yfinance (보조 수단) - start~end 사용
            try:
                time.sleep(1)  # API 요청 제한 방지
                df = yf.download("^KS11", start=start, end=end, interval="1d", progress=False, threads=False)
                out = _normalize_yf_close(df)
                if out:
                    logger.info("yfinance(^KS11)로 코스피 데이터 조회 성공")
                    return out
                logger.warning("yfinance로 코스피 데이터가 비어있습니다")
            except Exception as e:
                logger.warning("yfinance 실패(^KS11): %s", e)

            # 3) 정적 폴백
            logger.info("✅ 정적 데이터로 코스피 데이터 조회 성공")
            return self._get_static_kospi_data()

        except Exception as e:
            logger.error("코스피 데이터 조회 실패(최상위): %s", e)
            return self._get_static_kospi_data()

    def _get_static_kospi_data(self) -> List[Dict]:
        """
        최근 30일치 더미 데이터. 항상 리스트 반환.
        """
        base_price = 2500.0
        out: List[Dict] = []
        for i in range(30):
            d = datetime.now().date() - timedelta(days=29 - i)
            # 간단한 파형
            variation = ((i % 7) - 3) * 0.004  # 변동폭 소폭 축소
            out.append({"Date": d.strftime("%Y-%m-%d"), "Close": round(base_price * (1 + variation), 2)})
        return out

    def get_market_cap_top10(self) -> Dict:
        """
        시가총액 TOP10. 휴장일 보정 후 호출.
        실패 시 빈 리스트로 반환해 프런트가 정상적으로 렌더하도록 함.
        """
        try:
            time.sleep(1)  # API 요청 제한 방지
            ds = _nearest_business_day_str()
            df = stock.get_market_cap_by_ticker(ds, "KOSPI")
            if df is None or df.empty:
                logger.warning("시가총액 데이터 없음(%s)", ds)
                return {"시가총액_TOP10": []}

            df = df.reset_index()[["티커", "시가총액", "종가"]]
            
            # 기업명 조회 시 각 요청 사이에 약간의 딜레이
            기업명_list = []
            for ticker in df["티커"]:
                time.sleep(0.1)  # 짧은 대기 시간
                기업명_list.append(stock.get_market_ticker_name(ticker))
            df["기업명"] = 기업명_list
            
            top10 = (
                df.sort_values(by="시가총액", ascending=False)
                .head(10)[["기업명", "티커", "시가총액", "종가"]]
                .to_dict(orient="records")
            )
            logger.info("pykrx로 시가총액 TOP10 조회 성공(%s)", ds)
            return {"시가총액_TOP10": top10}
        except Exception as e:
            logger.warning("시가총액 데이터 조회 실패: %s", e)
            return {"시가총액_TOP10": []}

    def get_top_volume(self) -> List[Dict]:
        """
        거래량 TOP5. 휴장일 보정 후 호출. 실패 시 [].
        """
        try:
            time.sleep(1)  # API 요청 제한 방지
            ds = _nearest_business_day_str()
            df = stock.get_market_ohlcv(ds, "KOSPI")
            if df is None or df.empty:
                logger.warning("거래량 데이터 없음(%s)", ds)
                return []

            top5 = df.sort_values(by="거래량", ascending=False).head(5).copy()
            top5["종목코드"] = top5.index
            
            # 기업명 조회 시 각 요청 사이에 약간의 딜레이
            종목명_list = []
            for code in top5["종목코드"]:
                time.sleep(0.1)  # 짧은 대기 시간
                종목명_list.append(stock.get_market_ticker_name(code))
            top5["종목명"] = 종목명_list
            
            top5.reset_index(drop=True, inplace=True)
            out = top5[["종목명", "종목코드", "거래량"]].to_dict(orient="records")
            logger.info("pykrx로 거래량 TOP5 조회 성공(%s)", ds)
            return out
        except Exception as e:
            logger.warning("거래량 데이터 조회 실패: %s", e)
            return []

    def get_industry_analysis(self, name: str) -> Dict:
        """
        산업별 재무지표 분석 정보 조회. 파일 미존재/키 미존재도 예외 올리지 않고 404 메시지로 반환.
        """
        try:
            import json
            with open("산업별설명.json", encoding="utf-8") as f:
                data = json.load(f)

            name = name.strip()
            for item in data:
                if item.get("industry") == name:
                    return item
            return {"error": "해당 산업 정보가 없습니다."}
        except FileNotFoundError:
            return {"error": "산업별설명.json 파일을 찾을 수 없습니다."}
        except Exception as e:
            return {"error": f"서버 오류: {e}"}

    def get_company_metrics(self, name: str) -> Dict:
        """
        기업 재무지표 JSON 조회. 실패 시 에러 메시지 반환.
        """
        try:
            import json
            with open("기업별_재무지표.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get(name, {"error": "해당 기업 지표가 없습니다."})
        except Exception as e:
            return {"error": str(e)}


# 인스턴스 (라우터에서 import)
stock_service = StockService()
