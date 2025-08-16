import os
import asyncio
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import time
import traceback
from typing import List, Dict, Callable

logger = logging.getLogger("selenium_utils")

class SeleniumManager:
    def __init__(self):
        self.driver = None
        self.is_railway = os.getenv("RAILWAY_ENVIRONMENT") == "production"
        logger.info(f"Railway 환경 감지: {'Chromium 사용' if self.is_railway else 'Chrome 사용'}")
        
    async def create_driver(self):
        """WebDriver 생성"""
        try:
            chrome_options = Options()
            
            if self.is_railway:
                # Railway 환경: Chromium 사용
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--window-size=1920,1080")
                chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
                
                # Railway에서 Chromium 경로 설정
                chrome_options.binary_location = "/usr/bin/chromium-browser"
                
                # ChromeDriver 경로 설정
                driver_path = "/usr/local/bin/chromedriver"
                if os.path.exists(driver_path):
                    service = Service(driver_path)
                else:
                    # 시스템 PATH에서 찾기
                    service = Service("chromedriver")
            else:
                # 로컬 환경: 일반 Chrome 사용
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--window-size=1920,1080")
                chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
                
                # 로컬에서는 webdriver_manager 사용
                service = Service(ChromeDriverManager().install())
            
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("✅ WebDriver 생성 성공")
            return self.driver
            
        except Exception as e:
            logger.error(f"❌ WebDriver 생성 실패: {str(e)}")
            logger.error(traceback.format_exc())
            return None

    async def quit_driver(self):
        """WebDriver 종료"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                logger.info("✅ WebDriver 종료 완료")
        except Exception as e:
            logger.error(f"❌ WebDriver 종료 실패: {str(e)}")

    async def scrape_news(self, url: str, selector: str, max_items: int = 10, wait_time: int = 3):
        """다음뉴스 크롤링 (기존 로직 복구)"""
        try:
            # WebDriver 생성
            driver = await self.create_driver()
            if not driver:
                logger.error("WebDriver 생성 실패")
                return []
            
            try:
                # 페이지 로드
                driver.get(url)
                await asyncio.sleep(wait_time)  # 페이지 로딩 대기
                
                # 요소 찾기
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                
                news_data = []
                for i, element in enumerate(elements[:max_items]):
                    try:
                        # 제목과 링크 추출
                        title = element.text.strip()
                        href = element.get_attribute('href')
                        
                        if title and href:
                            news_data.append({
                                "title": title,
                                "url": href,
                                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                            })
                    except Exception as e:
                        logger.warning(f"뉴스 항목 파싱 실패: {e}")
                        continue
                
                logger.info(f"✅ 뉴스 크롤링 성공: {len(news_data)}개 항목")
                return news_data
                
            finally:
                await self.quit_driver()
                
        except Exception as e:
            logger.error(f"❌ 뉴스 크롤링 실패 ({url}): {str(e)}")
            return []

    async def scrape_with_custom_logic(self, url: str, custom_logic: Callable, wait_time: int = 3):
        """커스텀 스크래핑 로직 실행"""
        try:
            # WebDriver 생성
            driver = await self.create_driver()
            if not driver:
                logger.error("WebDriver 생성 실패")
                return []
            
            try:
                # 페이지 로드
                driver.get(url)
                await asyncio.sleep(wait_time)  # 페이지 로딩 대기
                
                # 커스텀 로직 실행
                result = custom_logic(driver)
                return result
                
            finally:
                await self.quit_driver()
                
        except Exception as e:
            logger.error(f"❌ 커스텀 스크래핑 실패 ({url}): {str(e)}")
            return []

# 전역 인스턴스
selenium_manager = SeleniumManager()