import os
import uvicorn
import time
from datetime import datetime, timedelta

def init_pykrx():
    try:
        from pykrx import stock
        today = datetime.now().strftime('%Y%m%d')
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
        # 삼성전자 주가 조회로 초기화
        result = stock.get_market_ohlcv_by_date(yesterday, today, "005930")
        print("✅ pykrx 초기화 성공")
    except Exception as e:
        print(f"⚠️ pykrx 초기화 중 오류 발생: {str(e)}")

def init_yfinance():
    try:
        import yfinance as yf
        # 삼성전자 주가 조회로 초기화
        ticker = yf.Ticker("005930.KS")
        ticker.info
        print("✅ yfinance 초기화 성공")
    except Exception as e:
        print(f"⚠️ yfinance 초기화 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    print("🔄 서비스 초기화 중...")
    time.sleep(5)  # MongoDB 연결 대기
    
    # 초기화 시도
    init_pykrx()
    init_yfinance()
    
    # 서버 시작
    port = int(os.getenv("PORT", 7000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"🚀 서버 시작 준비 중...")
    print(f"📍 호스트: {host}")
    print(f"🔌 포트: {port}")
    
    uvicorn.run("main:app", host=host, port=port)