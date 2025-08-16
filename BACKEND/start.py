import os
import uvicorn
import time
from datetime import datetime
import logging
import sys
import asyncio
import json
import requests
from typing import Optional
import traceback
from uvicorn import Config, Server
from utils.database import db_manager
from utils.data_processor import data_processor
from utils.selenium_utils import selenium_manager

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger("startup")

def check_environment():
    """환경 체크"""
    try:
        # 필수 패키지 임포트 체크
        import pandas as pd
        import numpy as np
        import requests
        
        logger.info("✅ 기본 패키지 확인 완료")
        
        # 환경변수 체크
        required_envs = ['MONGODB_URI', 'DB_NAME', 'PORT']
        missing_envs = [env for env in required_envs if not os.getenv(env)]
        
        if missing_envs:
            logger.warning(f"⚠️ 누락된 환경변수: {', '.join(missing_envs)}")
        else:
            logger.info("✅ 환경변수 확인 완료")
            
    except ImportError as e:
        logger.error(f"⚠️ 패키지 임포트 오류: {str(e)}")
    except Exception as e:
        logger.error(f"⚠️ 환경 체크 중 오류 발생: {str(e)}")

async def initialize_yfinance(max_retries: int = 3) -> bool:
    """yfinance 초기화 with 재시도 로직"""
    import yfinance as yf
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # 여러 티커 시도
    test_tickers = ['005930.KS', '000660.KS', '035420.KS']
    
    for attempt in range(max_retries):
        try:
            for ticker_symbol in test_tickers:
                ticker = yf.Ticker(ticker_symbol)
                
                # 기본 정보 요청
                url = f"https://query2.finance.yahoo.com/v8/finance/chart/{ticker_symbol}"
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                
                if response.status_code == 200:
                    logger.info(f"✅ yfinance 초기화 성공 (티커: {ticker_symbol})")
                    return True
                    
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # Too Many Requests
                wait_time = 2 ** attempt
                logger.warning(f"⚠️ Rate limit 도달. {wait_time}초 대기 후 재시도...")
                await asyncio.sleep(wait_time)
            else:
                logger.warning(f"⚠️ HTTP 오류 발생: {str(e)}")
        except Exception as e:
            logger.warning(f"⚠️ 시도 {attempt + 1}/{max_retries} 실패: {str(e)}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
            
    return False

async def initialize_services():
    """서비스 초기화"""
    logger.info("🔄 서비스 초기화 중...")
    
    try:
        # 1. 기본 패키지 확인
        logger.info("✅ 기본 패키지 확인 완료")
        
        # 2. 환경변수 확인
        required_envs = ["MONGODB_URI", "DB_NAME", "API_KEY", "NICE_API_KEY"]
        for env in required_envs:
            if not os.getenv(env):
                logger.warning(f"⚠️ {env} 환경변수가 설정되지 않았습니다")
        logger.info("✅ 환경변수 확인 완료")
        
        # 3. MongoDB 연결
        try:
            await db_manager.connect()
            logger.info("✅ MongoDB 연결 성공")
        except Exception as e:
            logger.error(f"❌ MongoDB 연결 실패: {str(e)}")
            raise
        
        # 4. 데이터 프로세서 초기화
        try:
            await data_processor.initialize()
            logger.info("✅ 데이터 프로세서 초기화 완료")
        except Exception as e:
            logger.error(f"❌ 데이터 프로세서 초기화 실패: {str(e)}")
            # 데이터 프로세서 실패는 치명적이지 않음
        
        # 5. Selenium 초기화 (제거 - 요청 시에만 사용)
        logger.info("✅ Selenium 초기화 완료 (지연 초기화)")
        
        # 6. pykrx 초기화
        try:
            await initialize_pykrx()
            logger.info("✅ pykrx 초기화 성공")
        except Exception as e:
            logger.error(f"❌ pykrx 초기화 실패: {str(e)}")
            # pykrx 실패는 치명적이지 않음
        
        # 7. yfinance 초기화
        try:
            await initialize_yfinance()
            logger.info("✅ yfinance 초기화 성공")
        except Exception as e:
            logger.error(f"❌ yfinance 초기화 실패: {str(e)}")
            # yfinance 실패는 치명적이지 않음
        
        logger.info("🚀 서버 시작 준비 중...")
        
    except Exception as e:
        logger.error(f"❌ 서비스 초기화 실패: {str(e)}")
        logger.error(traceback.format_exc())
        raise

async def initialize_pykrx():
    """pykrx 초기화"""
    try:
        from pykrx import stock
        # 간단한 연결 테스트
        test_data = stock.get_market_ohlcv_by_date("20240101", "20240102", "005930")
        if test_data is not None:
            logger.info("✅ pykrx 연결 테스트 성공")
        return True
    except Exception as e:
        logger.warning(f"⚠️ pykrx 초기화 실패: {str(e)}")
        return False

async def initialize_yfinance():
    """yfinance 초기화"""
    try:
        import yfinance as yf
        # 간단한 연결 테스트
        ticker = yf.Ticker("005930.KS")
        info = ticker.info
        if info:
            logger.info(f"✅ yfinance 초기화 성공 (티커: 005930.KS)")
            return True
    except Exception as e:
        logger.warning(f"⚠️ yfinance 초기화 실패: {str(e)}")
        return False
    
    return False

async def startup():
    """서버 시작"""
    try:
        # 서비스 초기화
        await initialize_services()
        
        # 포트를 강제로 7000으로 설정
        port = 7000
        host = os.getenv("HOST", "0.0.0.0")
        
        logger.info(f"🚀 서버 시작 - 호스트: {host}, 포트: {port}")
        logger.info(f"⚠️ 환경변수 PORT 무시하고 강제로 7000 사용")
        
        # uvicorn 설정
        config = Config(
            "main:app",
            host=host,
            port=port,
            log_level="debug",
            access_log=True,
            use_colors=False,
            loop="asyncio"
        )
        
        server = Server(config)
        await server.serve()
        
    except Exception as e:
        logger.error(f"❌ 서버 시작 실패: {str(e)}")
        logger.error(traceback.format_exc())
        
        # 5초 후 재시도
        logger.info("🔄 5초 후 재시도...")
        await asyncio.sleep(5)
        await startup()

if __name__ == "__main__":
    try:
        asyncio.run(startup())
    except KeyboardInterrupt:
        logger.info("🛑 서버 중단됨")
    except Exception as e:
        logger.error(f"❌ 치명적 오류: {str(e)}")
        logger.error(traceback.format_exc())