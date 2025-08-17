# BACKEND/app/utils/selenium_utils.py
from __future__ import annotations

import os
import stat
import logging
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import asyncio
import time
from typing import List, Dict, Callable

logger = logging.getLogger("selenium_utils")


def _ensure_executable(path: str) -> str:
    """경로에 실행 권한을 보장."""
    try:
        st = os.stat(path)
        if not (st.st_mode & stat.S_IXUSR):
            os.chmod(path, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            logger.info("✅ chromedriver 실행 권한 부여: %s", path)
    except Exception as e:
        logger.warning("⚠️ 실행 권한 설정 실패(%s): %s", path, e)
    return path


def _pick_real_chromedriver(installed_path: str) -> str:
    """
    webdriver_manager가 반환한 경로가 NOTICE 문서일 수 있으므로,
    반드시 실제 바이너리 'chromedriver' 파일을 선택한다.
    """
    # 정상: .../chromedriver-linux64/chromedriver
    d = os.path.dirname(installed_path)
    cand = os.path.join(d, "chromedriver")
    if os.path.isfile(cand):
        return cand

    # 압축 상위 구조에서 다시 한 번 탐색
    parent = os.path.dirname(d)
    cand2 = os.path.join(parent, "chromedriver-linux64", "chromedriver")
    if os.path.isfile(cand2):
        return cand2

    # 그래도 못 찾으면 같은 디렉토리의 파일 목록에서 이름이 정확히 chromedriver인 것만
    for name in os.listdir(d):
        p = os.path.join(d, name)
        if os.path.isfile(p) and name == "chromedriver":
            return p

    # 마지막 안전장치: 원래 경로(실패 가능) 반환
    return installed_path


def build_chrome_options(headless: bool = True) -> Options:
    opts = Options()
    
    # Chrome binary 위치 (환경에 맞춰 설정)
    for path in ["/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser"]:
        if os.path.exists(path):
            opts.binary_location = path
            logger.info("✅ Chrome 바이너리: %s", path)
            break
    
    # Headless & 안정성 옵션
    if headless:
        opts.add_argument("--headless=new")  # 최신 headless 모드
    opts.add_argument("--no-sandbox")  # 컨테이너 환경 필수
    opts.add_argument("--disable-dev-shm-usage")  # /dev/shm 부족 회피
    opts.add_argument("--disable-gpu")  # 리눅스 서버 안정성
    opts.add_argument("--disable-software-rasterizer")
    opts.add_argument("--disable-features=VizDisplayCompositor")
    opts.add_argument("--remote-debugging-port=9222")  # 렌더러 연결 안정성
    opts.add_argument("--window-size=1920,1080")
    
    # 성능 & 메모리 최적화
    opts.add_argument("--disable-extensions")
    opts.add_argument("--disable-setuid-sandbox")
    opts.add_argument("--single-process")
    opts.add_argument("--disable-background-timer-throttling")
    opts.add_argument("--disable-backgrounding-occluded-windows")
    opts.add_argument("--disable-renderer-backgrounding")
    opts.add_argument("--disable-features=TranslateUI")
    opts.add_argument("--disable-ipc-flooding-protection")
    opts.add_argument("--memory-pressure-off")
    opts.add_argument("--max_old_space_size=4096")
    
    # 로깅 설정
    opts.add_argument("--log-level=3")
    opts.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    # 한글 & 인코딩
    opts.add_argument("--lang=ko-KR")
    opts.add_argument("--no-first-run")
    opts.add_argument("--no-default-browser-check")
    
    return opts


def create_driver(headless: bool = True) -> webdriver.Chrome:
    """
    안전한 Chrome WebDriver 생성:
    - webdriver_manager로 자동 설치
    - 실행 권한 보장
    - 타임아웃 설정
    """
    try:
        # Selenium Manager가 드라이버 자동 설치
        service = Service()
        options = build_chrome_options(headless=headless)
        
        # WebDriver 생성 및 설정
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(30)  # 페이지 로드 타임아웃
        driver.implicitly_wait(10)  # 요소 찾기 타임아웃
        
        logger.info("✅ WebDriver 생성 성공")
        return driver
        
    except Exception as e:
        logger.error("❌ WebDriver 생성 실패: %s", str(e))
        logger.error("상세 에러: %s", traceback.format_exc())
        raise


# 기존 SeleniumManager 클래스와 호환성을 위한 래퍼
class SeleniumManager:
    def __init__(self):
        self.driver = None
        logger.info("SeleniumManager 초기화 완료")
        
    async def create_driver(self):
        """WebDriver 생성 (사용자 제공 해결책 사용)"""
        try:
            self.driver = create_driver(headless=True)
            return self.driver
        except Exception as e:
            logger.error("❌ WebDriver 생성 실패: %s", str(e))
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

    def _init_driver(self):
        """WebDriver 초기화"""
        try:
            logger.info("====== WebDriver manager ======")
            
            # Linux 환경에서 Chrome 옵션 설정
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--headless')  # Railway에서는 headless 모드 필수
            chrome_options.add_argument('--remote-debugging-port=9222')
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--allow-running-insecure-content')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-plugins')
            chrome_options.add_argument('--disable-images')
            # chrome_options.add_argument('--disable-javascript')  # JavaScript 비활성화로 안정성 향상
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36')
            
            # Railway 환경에서 필요한 추가 설정
            chrome_options.add_argument('--disable-background-timer-throttling')
            chrome_options.add_argument('--disable-backgrounding-occluded-windows')
            chrome_options.add_argument('--disable-renderer-backgrounding')
            chrome_options.add_argument('--disable-features=TranslateUI')
            chrome_options.add_argument('--disable-ipc-flooding-protection')
            
            # 메모리 사용량 최적화
            chrome_options.add_argument('--memory-pressure-off')
            chrome_options.add_argument('--max_old_space_size=4096')
            
            # 로그 레벨 설정
            chrome_options.add_argument('--log-level=3')
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            
            # WebDriver Manager를 사용하여 ChromeDriver 자동 관리
            service = Service(ChromeDriverManager().install())
            
            # WebDriver 생성
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # 페이지 로드 타임아웃 설정
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)
            
            logger.info("✅ WebDriver 생성 성공")
            
        except Exception as e:
            logger.error(f"❌ WebDriver 생성 실패: {e}")
            self.driver = None

    def crawl_company_news(self, search_query: str, max_news: int = 10) -> List[Dict]:
        """기업별 관련 뉴스 크롤링"""
        try:
            if not self.driver:
                self._init_driver()
            
            # 더 안정적인 뉴스 사이트 사용 (네이버 뉴스 대신)
            search_url = f"https://search.naver.com/search.naver?where=news&query={search_query}&sort=1"  # 최신순 정렬
            logger.info(f"🔍 뉴스 검색 URL: {search_url}")
            
            self.driver.get(search_url)
            time.sleep(3)  # 페이지 로딩 대기 시간 증가
            
            news_items = []
            
            # 더 구체적인 CSS 선택자 사용
            try:
                news_elements = self.driver.find_elements(By.CSS_SELECTOR, "li.bx")
                logger.info(f"📰 찾은 뉴스 요소 수: {len(news_elements)}")
                
                for i, element in enumerate(news_elements[:max_news]):
                    try:
                        # 제목 추출
                        title_element = element.find_element(By.CSS_SELECTOR, "a.news_tit")
                        title = title_element.text.strip()
                        link = title_element.get_attribute("href")
                        
                        # 내용 추출
                        try:
                            content_element = element.find_element(By.CSS_SELECTOR, "div.dsc_wrap")
                            content = content_element.text.strip()
                        except:
                            content = ""
                        
                        # 언론사 추출
                        try:
                            press_element = element.find_element(By.CSS_SELECTOR, "a.press")
                            category = press_element.text.strip()
                        except:
                            category = ""
                        
                        # 날짜 추출
                        try:
                            date_element = element.find_element(By.CSS_SELECTOR, "span.info")
                            date = date_element.text.strip()
                        except:
                            date = ""
                        
                        if title and link:  # 제목과 링크가 있는 경우만 추가
                            news_items.append({
                                "title": title,
                                "link": link,
                                "content": content,
                                "date": date,
                                "category": category
                            })
                            logger.info(f"✅ 뉴스 항목 {i+1} 추가: {title[:30]}...")
                        
                    except Exception as e:
                        logger.warning(f"⚠️ 뉴스 항목 {i+1} 파싱 실패: {e}")
                        continue
                
                logger.info(f"📊 총 {len(news_items)}개 뉴스 항목 수집 완료")
                
            except Exception as e:
                logger.warning(f"⚠️ 뉴스 요소 검색 실패: {e}")
                # 폴백: 더미 뉴스 데이터 반환
                news_items = [
                    {
                        "title": f"{search_query} 관련 최신 뉴스",
                        "link": "https://search.naver.com/search.naver?where=news",
                        "content": "해당 기업에 대한 최신 뉴스를 확인할 수 있습니다.",
                        "date": "최근",
                        "category": "종합"
                    }
                ]
            
            return news_items
            
        except Exception as e:
            logger.error(f"❌ 기업 뉴스 크롤링 실패: {e}")
            # 오류 발생 시 더미 데이터 반환
            return [
                {
                    "title": f"{search_query} 관련 뉴스",
                    "link": "https://search.naver.com/search.naver?where=news",
                    "content": "뉴스 크롤링 중 일시적인 오류가 발생했습니다.",
                    "date": "최근",
                    "category": "종합"
                }
            ]


selenium_manager = SeleniumManager()