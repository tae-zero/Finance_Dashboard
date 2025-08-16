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

    async def scrape_news(self, url: str, selector: str, max_items: int = 10):
        """뉴스 스크래핑 (여러 방법 시도)"""
        try:
            # 1차 시도: 원본 URL
            news_data = await self._try_scrape_url(url, selector, max_items)
            if news_data:
                return news_data
            
            # 2차 시도: 대체 URL들
            fallback_urls = [
                "https://finance.naver.com/news/mainnews.naver",
                "https://finance.naver.com/news/news_list.naver",
                "https://finance.naver.com/sise/sise_index.naver?code=KOSPI"
            ]
            
            for fallback_url in fallback_urls:
                try:
                    news_data = await self._try_scrape_url(fallback_url, ".news_list a", max_items)
                    if news_data:
                        logger.info(f"✅ 대체 URL에서 뉴스 수집 성공: {fallback_url}")
                        return news_data
                except Exception as e:
                    logger.warning(f"대체 URL 실패 ({fallback_url}): {e}")
                    continue
            
            # 3차 시도: 폴백 데이터
            logger.warning("⚠️ 모든 크롤링 시도 실패. 폴백 데이터 사용")
            return self._get_fallback_news()
                    
        except Exception as e:
            logger.error(f"❌ 뉴스 스크래핑 실패 ({url}): {str(e)}")
            return self._get_fallback_news()

    async def _try_scrape_url(self, url: str, selector: str, max_items: int = 10):
        """특정 URL에서 뉴스 스크래핑 시도"""
        try:
            import aiohttp
            from bs4 import BeautifulSoup
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1"
                }
                
                async with session.get(url, headers=headers, timeout=30) as response:
                    if response.status != 200:
                        return None
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # 여러 선택자 시도
                    selectors_to_try = [
                        selector,
                        ".news_list a",
                        ".article_list a", 
                        ".main_news a",
                        "a[href*='news']"
                    ]
                    
                    news_data = []
                    for sel in selectors_to_try:
                        links = soup.select(sel)
                        if links:
                            for i, link in enumerate(links[:max_items]):
                                try:
                                    title = link.get_text(strip=True)
                                    href = link.get('href', '')
                                    
                                    if title and len(title.strip()) > 5:
                                        # 상대 URL을 절대 URL로 변환
                                        if href.startswith('/'):
                                            href = f"https://finance.naver.com{href}"
                                        elif not href.startswith('http'):
                                            href = f"https://finance.naver.com/{href}"
                                        
                                        news_data.append({
                                            "title": title,
                                            "url": href,
                                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                                        })
                                except Exception as e:
                                    continue
                            
                            if news_data:
                                logger.info(f"✅ 선택자 '{sel}'에서 {len(news_data)}개 뉴스 수집")
                                return news_data
                    
                    return None
                    
        except Exception as e:
            logger.warning(f"URL 스크래핑 실패 ({url}): {e}")
            return None

    def _get_fallback_news(self):
        """폴백 뉴스 데이터 (크롤링 실패 시)"""
        return [
            {
                "title": "금융시장 동향 분석",
                "url": "https://finance.naver.com",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                "title": "주요 기업 실적 발표",
                "url": "https://finance.naver.com",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                "title": "투자자 심리 지표",
                "url": "https://finance.naver.com",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        ]

# 전역 인스턴스
selenium_manager = SeleniumManager()