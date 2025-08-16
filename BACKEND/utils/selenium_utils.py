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

logger = logging.getLogger("selenium_utils")

def circuit_breaker(max_failures: int = 3, reset_time: int = 60):
    """회로 차단기 데코레이터"""
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
        self.CACHE_DURATION = 600  # 10분

    def _get_cached_data(self, key: str) -> Optional[Dict]:
        """캐시된 데이터 조회"""
        if key in self._cache:
            timestamp, data = self._cache[key]
            if time.time() - timestamp < self.CACHE_DURATION:
                return data
        return None

    def _set_cached_data(self, key: str, data: Dict):
        """데이터 캐시에 저장"""
        self._cache[key] = (time.time(), data)

    async def create_driver(self) -> webdriver.Chrome:
        """Chrome WebDriver 생성"""
        try:
            def _create():
                options = Options()
                options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-gpu')
                options.add_argument('--window-size=1920,1080')
                options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
                
                driver = webdriver.Chrome(options=options)
                driver.set_page_load_timeout(20)
                return driver

            return await asyncio.to_thread(_create)
        except Exception as e:
            logger.error(f"WebDriver 생성 실패: {str(e)}")
            raise HTTPException(status_code=503, detail=f"브라우저 초기화 실패: {str(e)}")

    async def get_driver(self) -> webdriver.Chrome:
        """WebDriver 인스턴스 가져오기 (없으면 생성)"""
        if not self.driver:
            self.driver = await self.create_driver()
        return self.driver

    async def quit_driver(self):
        """WebDriver 종료"""
        if self.driver:
            try:
                await asyncio.to_thread(self.driver.quit)
            except Exception as e:
                logger.warning(f"WebDriver 종료 중 오류: {str(e)}")
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
                logger.warning(f"페이지 로딩 실패 (재시도 {attempt + 1}/{max_retries}): {str(e)}")
                if attempt == max_retries - 1:
                    raise HTTPException(status_code=503, detail=f"페이지 로딩 실패: {str(e)}")
                await self.quit_driver()
                await asyncio.sleep(2 ** attempt)
        return False

    @circuit_breaker(max_failures=3, reset_time=60)
    async def scrape_news(self, url: str, selector: str, max_items: int = 10) -> List[Dict]:
        """뉴스 데이터 스크래핑"""
        cache_key = f"news_{url}_{selector}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data

        try:
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
            # 마지막 성공 데이터 반환 시도
            last_data = self._get_cached_data(cache_key)
            if last_data:
                logger.info(f"캐시된 마지막 뉴스 데이터 반환 ({url})")
                return last_data
            raise HTTPException(status_code=503, detail=f"뉴스 데이터 수집 실패: {str(e)}")
        finally:
            await self.quit_driver()

    async def __aenter__(self):
        """비동기 컨텍스트 매니저 진입"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료"""
        await self.quit_driver()

# 싱글톤 인스턴스 생성
selenium_manager = SeleniumManager()