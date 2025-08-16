import os
import uvicorn
import time
from datetime import datetime, timedelta

def init_pykrx():
    try:
        from pykrx import stock
        import pandas as pd
        
        # 오늘 날짜
        today = datetime.now()
        # 1주일 전 날짜
        week_ago = today - timedelta(days=7)
        
        # 날짜 형식 변환
        today_str = today.strftime('%Y%m%d')
        week_ago_str = week_ago.strftime('%Y%m%d')
        
        # 코스피 지수로 초기화 (개별 종목 대신)
        result = stock.get_index_ohlcv_by_date(week_ago_str, today_str, "1001")
        if not result.empty:
            print("✅ pykrx 초기화 성공")
        else:
            print("⚠️ pykrx 데이터 없음")
    except Exception as e:
        print(f"⚠️ pykrx 초기화 중 오류 발생: {str(e)}")
        print("⚠️ pykrx 초기화 실패, 서비스 일부 기능이 제한될 수 있습니다.")

def init_yfinance():
    try:
        import yfinance as yf
        import time
        
        # 요청 간격 조절
        time.sleep(2)
        
        # 코스피 지수로 초기화 (개별 종목 대신)
        ticker = yf.Ticker("^KS11")
        history = ticker.history(period="1d")
        
        if not history.empty:
            print("✅ yfinance 초기화 성공")
        else:
            print("⚠️ yfinance 데이터 없음")
    except Exception as e:
        print(f"⚠️ yfinance 초기화 중 오류 발생: {str(e)}")
        print("⚠️ yfinance 초기화 실패, 서비스 일부 기능이 제한될 수 있습니다.")

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