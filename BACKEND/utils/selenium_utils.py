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
                # Railway 환경: Google Chrome 사용 (Dockerfile에서 설치)
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--window-size=1920,1080")
                chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
                chrome_options.add_argument("--disable-blink-features=AutomationControlled")
                chrome_options.add_argument("--disable-extensions")
                chrome_options.add_argument("--disable-infobars")
                chrome_options.add_argument("--ignore-certificate-errors")
                chrome_options.add_argument("--disable-popup-blocking")
                
                # Dockerfile에서 설치한 Google Chrome 경로 (여러 경로 시도)
                chrome_paths = [
                    "/usr/bin/google-chrome",
                    "/usr/bin/google-chrome-stable",
                    "/opt/google/chrome/chrome"
                ]
                
                chrome_found = False
                for chrome_path in chrome_paths:
                    if os.path.exists(chrome_path):
                        chrome_options.binary_location = chrome_path
                        logger.info(f"✅ Chrome 발견: {chrome_path}")
                        chrome_found = True
                        break
                
                if not chrome_found:
                    logger.warning("⚠️ Chrome 경로를 찾을 수 없습니다. 기본 경로 사용")
                
                # ChromeDriver 경로 설정 (Dockerfile에서 설치)
                driver_paths = [
                    "/usr/local/bin/chromedriver",  # Dockerfile에서 설치한 경로
                    "/usr/bin/chromedriver",
                    "chromedriver"  # 시스템 PATH에서 찾기
                ]
                
                service = None
                for driver_path in driver_paths:
                    try:
                        if os.path.exists(driver_path):
                            service = Service(driver_path)
                            logger.info(f"✅ ChromeDriver 발견: {driver_path}")
                            break
                        else:
                            # 시스템 PATH에서 찾기 시도
                            service = Service(driver_path)
                            logger.info(f"✅ 시스템 PATH에서 ChromeDriver 사용: {driver_path}")
                            break
                    except Exception as e:
                        logger.warning(f"ChromeDriver 경로 실패 ({driver_path}): {e}")
                        continue
                
                if not service:
                    raise Exception("사용 가능한 ChromeDriver를 찾을 수 없습니다")
                    
            else:
                # 로컬 환경: 일반 Chrome 사용
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--window-size=1920,1080")
                chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
                
                # 로컬에서는 webdriver_manager 사용
                try:
                    service = Service(ChromeDriverManager().install())
                except Exception as e:
                    logger.warning(f"webdriver_manager 실패: {e}")
                    service = Service("chromedriver")
            
            # WebDriver 생성
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