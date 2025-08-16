#!/bin/bash

# pykrx 초기화
echo "🔄 pykrx 초기화 중..."
python -c "from pykrx import stock; stock.get_market_ohlcv_by_date('20240101', '20240101', '005930')"

# yfinance 초기화
echo "🔄 yfinance 초기화 중..."
python -c "import yfinance as yf; yf.download('005930.KS', start='2024-01-01', end='2024-01-02')"

# FastAPI 서버 시작
echo "🚀 서버 시작..."
uvicorn main:app --host 0.0.0.0 --port $PORT
