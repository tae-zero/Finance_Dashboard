import os
import uvicorn
import time
from datetime import datetime
import logging
import sys

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

def initialize_services():
    """서비스 초기화"""
    try:
        # MongoDB 연결 체크
        from utils.database import db_manager
        db_manager.get_database()
        logger.info("✅ MongoDB 연결 성공")

        # 데이터 프로세서 초기화
        from utils.data_processor import data_processor
        logger.info("✅ 데이터 프로세서 초기화 완료")

        # Selenium 매니저 초기화
        from utils.selenium_utils import selenium_manager
        selenium_manager.create_driver()
        selenium_manager.quit_driver()
        logger.info("✅ Selenium 초기화 완료")

        # pykrx 초기화 테스트
        try:
            from pykrx import stock
            stock.get_market_ticker_list(datetime.now().strftime("%Y%m%d"))
            logger.info("✅ pykrx 초기화 성공")
        except Exception as e:
            logger.warning(f"⚠️ pykrx 초기화 실패: {str(e)}")
            logger.warning("⚠️ 더미 데이터를 사용합니다.")

        # yfinance 초기화 테스트
        try:
            import yfinance as yf
            yf.Ticker("005930.KS").info
            logger.info("✅ yfinance 초기화 성공")
        except Exception as e:
            logger.warning(f"⚠️ yfinance 초기화 실패: {str(e)}")
            logger.warning("⚠️ 더미 데이터를 사용합니다.")

    except Exception as e:
        logger.error(f"⚠️ 서비스 초기화 중 오류 발생: {str(e)}")
        logger.warning("⚠️ 일부 기능이 제한될 수 있습니다.")

if __name__ == "__main__":
    logger.info("🔄 서비스 초기화 중...")
    
    # 환경 체크
    check_environment()
    
    # 서비스 초기화
    initialize_services()
    
    # 서버 시작
    port = int(os.getenv("PORT", 7000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"🚀 서버 시작 준비 중...")
    logger.info(f"📍 호스트: {host}")
    logger.info(f"🔌 포트: {port}")
    
    try:
        uvicorn.run("main:app", host=host, port=port, log_level="info")
    except Exception as e:
        logger.error(f"❌ 서버 시작 실패: {e}")
        raise e