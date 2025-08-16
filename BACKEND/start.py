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
    try:
        # MongoDB 연결 체크
        from utils.database import db_manager
        if db_manager.is_connected():
            logger.info("✅ MongoDB 연결 성공")

        # 데이터 프로세서 초기화
        from utils.data_processor import data_processor
        logger.info("✅ 데이터 프로세서 초기화 완료")

        # Selenium 매니저 초기화
        from utils.selenium_utils import selenium_manager
        try:
            driver = await selenium_manager.create_driver()
            await selenium_manager.quit_driver()
            logger.info("✅ Selenium 초기화 완료")
        except Exception as e:
            logger.warning(f"⚠️ Selenium 초기화 실패: {str(e)}")

        # pykrx 초기화 테스트
        try:
            from pykrx import stock
            stock.get_market_ticker_list(datetime.now().strftime("%Y%m%d"))
            logger.info("✅ pykrx 초기화 성공")
        except Exception as e:
            logger.warning(f"⚠️ pykrx 초기화 실패: {str(e)}")
            logger.warning("⚠️ 더미 데이터를 사용합니다.")

        # yfinance 초기화 테스트
        if await initialize_yfinance():
            logger.info("✅ yfinance 초기화 및 연결 테스트 완료")
        else:
            logger.warning("⚠️ yfinance 초기화 실패 - 더미 데이터를 사용합니다.")

    except Exception as e:
        logger.error(f"⚠️ 서비스 초기화 중 오류 발생: {str(e)}")
        logger.warning("⚠️ 일부 기능이 제한될 수 있습니다.")

async def startup():
    """서버 시작 전 초기화"""
    logger.info("🔄 서비스 초기화 중...")
    
    # 환경 체크
    check_environment()
    
    # 서비스 초기화
    await initialize_services()
    
    # 서버 시작
    port = int(os.getenv("PORT", 7000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"🚀 서버 시작 준비 중...")
    logger.info(f"📍 호스트: {host}")
    logger.info(f"🔌 포트: {port}")
    
    # uvicorn 설정
    config = uvicorn.Config(
        "main:app", 
        host=host, 
        port=port, 
        log_level="info",
        access_log=True,
        use_colors=False,
        loop="asyncio"
    )
    
    server = uvicorn.Server(config)
    
    try:
        logger.info("🚀 서버 시작 중...")
        await server.serve()
    except Exception as e:
        logger.error(f"❌ 서버 시작 실패: {e}")
        logger.error(traceback.format_exc())
        # 서버 실패 시에도 프로세스 유지
        logger.info("🔄 서버 재시작 시도 중...")
        await asyncio.sleep(5)
        await startup()  # 재귀적으로 재시작

if __name__ == "__main__":
    asyncio.run(startup())