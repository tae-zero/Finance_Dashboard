from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from fastapi import HTTPException
import logging
import time
from typing import List, Dict, Optional
from datetime import datetime
import asyncio
from functools import wraps
import aiohttp
import json
import os  # os 모듈 추가

logger = logging.getLogger("selenium_utils")

class SeleniumManager:
    def __init__(self):
        self.driver = None
        self._cache = {}
        self.CACHE_DURATION = 600  # 10분
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    async def create_driver(self) -> webdriver.Chrome:
        """Chrome WebDriver 생성"""
        try:
            def _create():
                options = Options()
                options.add_argument('--headless=new')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-gpu')
                options.add_argument('--window-size=1920,1080')
                options.add_argument(f'user-agent={self.headers["User-Agent"]}')
                options.add_argument('--disable-blink-features=AutomationControlled')
                
                # Railway 환경 체크
                if os.getenv("RAILWAY_ENVIRONMENT"):
                    logger.info("Railway 환경 감지: Chromium 사용")
                    options.binary_location = "/usr/bin/chromium-browser"
                else:
                    logger.info("로컬 환경 감지: Chrome 사용")
                
                driver = webdriver.Chrome(options=options)
                driver.set_page_load_timeout(30)
                return driver

            return await asyncio.to_thread(_create)
        except Exception as e:
            logger.error(f"WebDriver 생성 실패: {str(e)}")
            logger.error(f"현재 환경: RAILWAY_ENVIRONMENT={os.getenv('RAILWAY_ENVIRONMENT')}")
            raise HTTPException(status_code=503, detail=f"브라우저 초기화 실패: {str(e)}")

    # ... (나머지 코드는 동일)