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
import time
import traceback
from typing import List, Dict, Callable

logger = logging.getLogger("selenium_utils")

class SeleniumManager:
    def __init__(self):
        self.driver = None
        self.is_railway = os.getenv("RAILWAY_ENVIRONMENT") == "production"
        logger.info("Railway 환경 감지: %s", "Chromium 사용" if self.is_railway else "Chrome 사용")
        
    async def create_driver(self):
        """WebDriver 생성 (Railway 환경 최적화)"""
        try:
            chrome_options = Options()
            
            # Railway 환경 최적화 옵션
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-infobars")
            chrome_options.add_argument("--ignore-certificate-errors")
            chrome_options.add_argument("--disable-popup-blocking")
            chrome_options.add_argument("--remote-debugging-port=9222")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            
            if self.is_railway:
                # Railway 환경: 환경변수로 Chrome 바이너리 지정
                chrome_bin = os.getenv("CHROME_BIN", "/usr/bin/google-chrome")
                if os.path.exists(chrome_bin):
                    chrome_options.binary_location = chrome_bin
                    logger.info("✅ Chrome 바이너리 설정: %s", chrome_bin)
                else:
                    logger.warning("⚠️ Chrome 바이너리를 찾을 수 없음: %s", chrome_bin)
            
            # ChromeDriver 경로 설정 (우선순위 순)
            chromedriver_paths = [
                os.getenv("CHROMEDRIVER_PATH"),  # 환경변수
                "/usr/local/bin/chromedriver",   # Docker 설치 경로
                "/usr/bin/chromedriver",         # 시스템 설치 경로
                "chromedriver"                   # PATH에서 찾기
            ]
            
            service = None
            for path in chromedriver_paths:
                if path and os.path.exists(path):
                    try:
                        # 실행 권한 확인 및 설정
                        if os.path.isfile(path):
                            os.chmod(path, 0o755)
                            service = Service(path)
                            logger.info("✅ ChromeDriver 사용: %s", path)
                            break
                    except Exception as e:
                        logger.debug("ChromeDriver 경로 실패 (%s): %s", path, e)
                        continue
            
            if not service:
                raise FileNotFoundError("사용 가능한 ChromeDriver를 찾을 수 없습니다")
            
            # WebDriver 생성
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("✅ WebDriver 생성 성공")
            return self.driver
            
        except Exception as e:
            logger.error("❌ WebDriver 생성 실패: %s", str(e))
            logger.error("Traceback:\n%s", traceback.format_exc())
            return None

    async def quit_driver(self):
        """WebDriver 종료"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                logger.info("✅ WebDriver 종료 완료")
        except Exception as e:
            logger.error("❌ WebDriver 종료 실패: %s", str(e))

    async def scrape_news(self, url: str, selector: str, max_items: int = 10, wait_time: int = 3):
        """다음뉴스 크롤링"""
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
                        logger.warning("뉴스 항목 파싱 실패: %s", e)
                        continue
                
                logger.info("✅ 뉴스 크롤링 성공: %d개 항목", len(news_data))
                return news_data
                
            finally:
                await self.quit_driver()
                
        except Exception as e:
            logger.error("❌ 뉴스 크롤링 실패 (%s): %s", url, str(e))
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
            logger.error("❌ 커스텀 스크래핑 실패 (%s): %s", url, str(e))
            return []

selenium_manager = SeleniumManager()