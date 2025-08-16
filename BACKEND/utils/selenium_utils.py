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
import os

logger = logging.getLogger("selenium_utils")

def circuit_breaker(max_failures: int = 3, reset_time: int = 60):
    """서킷 브레이커 데코레이터"""
    def decorator(func):
        failures = 0
        last_failure_time = 0
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            nonlocal failures, last_failure_time
            
            if time.time() - last_failure_time > reset_time:
                failures = 0
                
            if failures >= max_failures:
                if time.time() - last_failure_time <= reset_time:
                    raise HTTPException(
                        status_code=503,
                        detail="서비스가 일시적으로 불안정합니다. 잠시 후 다시 시도해주세요."
                    )
                failures = 0
                
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                failures += 1
                last_failure_time = time.time()
                raise e
                
        return wrapper
    return decorator

class SeleniumManager:
    def __init__(self):
        self.driver = None
        self._cache = {}
        self.CACHE_DURATION = 600
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
                options.add_argument('--disable-extensions')
                options.add_argument('--disable-infobars')
                options.add_argument('--ignore-certificate-errors')
                options.add_argument('--disable-popup-blocking')
                
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

    async def get_driver(self) -> webdriver.Chrome:
        """WebDriver 가져오기 (없으면 생성)"""
        if not self.driver:
            self.driver = await self.create_driver()
        return self.driver

    async def quit_driver(self):
        """WebDriver 종료"""
        if self.driver:
            try:
                await asyncio.to_thread(self.driver.quit)
            except Exception as e:
                logger.warning(f"드라이버 종료 중 오류: {str(e)}")
            finally:
                self.driver = None

    async def safe_get(self, url: str, max_retries: int = 3) -> bool:
        """안전한 페이지 로딩"""
        for attempt in range(max_retries):
            try:
                driver = await self.get_driver()
                await asyncio.to_thread(driver.get, url)
                return True
            except Exception as e:
                logger.warning(f"페이지 로딩 실패 (시도 {attempt + 1}/{max_retries}): {str(e)}")
                if attempt == max_retries - 1:
                    return False
                await asyncio.sleep(1)
        return False

    async def scrape_news_with_requests(self, url: str) -> List[Dict]:
        """requests 기반 뉴스 스크래핑 (1차 시도)"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, timeout=10) as response:
                    if response.status == 200:
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(await response.text(), 'html.parser')
                        news_items = []
                        
                        for item in soup.select('.news_list a'):
                            title = item.text.strip()
                            link = item.get('href', '')
                            if title and link:
                                news_items.append({
                                    "title": title,
                                    "link": link if link.startswith('http') else f"https://finance.naver.com{link}",
                                    "date": datetime.now().strftime("%Y-%m-%d")
                                })
                        return news_items
                    else:
                        raise HTTPException(status_code=response.status, detail="뉴스 데이터 조회 실패")
        except Exception as e:
            logger.error(f"뉴스 스크래핑 실패 (requests): {str(e)}")
            raise HTTPException(status_code=503, detail=str(e))

    @circuit_breaker(max_failures=3, reset_time=60)
    async def scrape_news(self, url: str, selector: str, max_items: int = 10) -> List[Dict]:
        """뉴스 스크래핑 (requests 우선, Selenium 폴백)"""
        cache_key = f"news_{url}_{selector}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data

        try:
            # 1차 시도: requests 기반 스크래핑
            try:
                news_data = await self.scrape_news_with_requests(url)
                if news_data:
                    self._set_cached_data(cache_key, news_data)
                    return news_data
            except Exception as e:
                logger.warning(f"Requests 스크래핑 실패, Selenium으로 전환: {str(e)}")

            # 2차 시도: Selenium 기반 스크래핑
            if not await self.safe_get(url):
                raise HTTPException(status_code=503, detail="페이지 로딩 실패")

            driver = await self.get_driver()
            
            def _scrape():
                wait = WebDriverWait(driver, 10)
                elements = wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
                )
                
                news_data = []
                for element in elements[:max_items]:
                    try:
                        title = element.text.strip()
                        link = element.get_attribute('href')
                        if title and link:
                            news_data.append({
                                "title": title,
                                "link": link,
                                "date": datetime.now().strftime("%Y-%m-%d")
                            })
                    except Exception as e:
                        logger.warning(f"뉴스 항목 파싱 실패: {str(e)}")
                        continue
                        
                return news_data

            news_data = await asyncio.to_thread(_scrape)
            
            if not news_data:
                raise HTTPException(status_code=404, detail="뉴스 데이터가 없습니다")

            self._set_cached_data(cache_key, news_data)
            return news_data

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"뉴스 스크래핑 실패 ({url}): {str(e)}")
            raise HTTPException(status_code=503, detail=f"뉴스 데이터 수집 실패: {str(e)}")
        finally:
            await self.quit_driver()

    def _get_cached_data(self, key: str) -> Optional[Dict]:
        """캐시된 데이터 가져오기"""
        if key in self._cache:
            data, timestamp = self._cache[key]
            if time.time() - timestamp < self.CACHE_DURATION:
                return data
            else:
                del self._cache[key]
        return None

    def _set_cached_data(self, key: str, data: Dict):
        """데이터 캐시에 저장"""
        self._cache[key] = (data, time.time())

    async def __aenter__(self):
        """비동기 컨텍스트 매니저 진입"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료"""
        await self.quit_driver()

# 전역 인스턴스 생성
selenium_manager = SeleniumManager()