from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

class SeleniumManager:
    @staticmethod
    def create_driver(headless=True, additional_options=None):
        """Chrome 드라이버 생성"""
        options = Options()
        
        # Chromium 옵션 설정
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.binary_location = "/usr/bin/chromium"
        """Chrome 드라이버 생성"""
        options = Options()
        
        if headless:
            options.add_argument('--headless')
        
        # 기본 옵션
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--window-size=1920x1080')
        
        # 추가 옵션이 있으면 적용
        if additional_options:
            for option in additional_options:
                options.add_argument(option)
        
        # 드라이버 생성
        try:
            # ChromeDriver 자동 설치 (더 안정적인 방법)
            driver = webdriver.Chrome(options=options)
        except Exception as e:
            print(f"ChromeDriver 오류: {e}")
            try:
                # 대체 방법: ChromeDriverManager 사용
                driver = webdriver.Chrome(
                    service=Service(ChromeDriverManager().install()), 
                    options=options
                )
            except Exception as e2:
                print(f"ChromeDriverManager 오류: {e2}")
                raise Exception(f"ChromeDriver 초기화 실패: {e}")
        
        return driver
    
    @staticmethod
    def scrape_news(url, selector, max_items=5, wait_time=2):
        """뉴스 스크래핑 공통 함수"""
        driver = SeleniumManager.create_driver()
        
        try:
            driver.get(url)
            time.sleep(wait_time)
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            a_tags = soup.select(selector)
            
            news_list = [
                {"title": a.text.strip(), "link": a['href']} 
                for a in a_tags[:max_items]
            ]
            
            return news_list
            
        finally:
            driver.quit()
    
    @staticmethod
    def scrape_with_custom_logic(url, custom_function, wait_time=2):
        """커스텀 로직으로 스크래핑"""
        driver = SeleniumManager.create_driver()
        
        try:
            driver.get(url)
            time.sleep(wait_time)
            
            return custom_function(driver)
            
        finally:
            driver.quit()
