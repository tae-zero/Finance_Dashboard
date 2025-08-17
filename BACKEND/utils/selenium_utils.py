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
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--window-size=1280,800")
    opts.add_argument("--remote-debugging-port=9222")
    opts.add_argument("--lang=ko-KR")

    chrome_bin = os.getenv("GOOGLE_CHROME_BIN", "/usr/bin/google-chrome")
    if os.path.exists(chrome_bin):
        opts.binary_location = chrome_bin
        logger.info("✅ Chrome 바이너리: %s", chrome_bin)
    else:
        logger.warning("⚠️ Chrome 바이너리 미발견: %s", chrome_bin)
    return opts


def create_driver(headless: bool = True) -> webdriver.Chrome:
    """
    안전한 Chrome WebDriver 생성:
    - webdriver_manager 설치 경로에서 실제 'chromedriver'만 집어 사용
    - 실행 권한 보장
    """
    logger.info("====== WebDriver manager ======")
    installed = ChromeDriverManager().install()
    logger.info("웹드라이버 설치 경로(원본): %s", installed)

    driver_path = _pick_real_chromedriver(installed)
    if os.path.basename(driver_path) != "chromedriver":
        logger.error("❌ 잘못된 드라이버 경로 선택: %s", driver_path)
    driver_path = _ensure_executable(driver_path)
    logger.info("✅ 최종 chromedriver 경로: %s", driver_path)

    service = Service(executable_path=driver_path)
    options = build_chrome_options(headless=headless)

    try:
        driver = webdriver.Chrome(service=service, options=options)
        logger.info("✅ WebDriver 생성 성공")
        return driver
    except OSError as e:
        # 아키텍처 불일치(arm64 vs amd64) 가능성 등
        logger.error("❌ WebDriver 생성 실패(OSerror): %s", e)
        raise
    except Exception as e:
        logger.error("❌ WebDriver 생성 실패: %s", e, exc_info=True)
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

    def crawl_company_news(self, search_query: str, max_news: int = 10) -> List[Dict]:
        """기업별 관련 뉴스 크롤링"""
        try:
            if not self.driver:
                self._init_driver()
            
            # 네이버 뉴스에서 검색
            search_url = f"https://search.naver.com/search.naver?where=news&query={search_query}"
            self.driver.get(search_url)
            time.sleep(2)
            
            news_items = []
            news_elements = self.driver.find_elements(By.CSS_SELECTOR, ".news_wrap.api_ani_send")
            
            for i, element in enumerate(news_elements[:max_news]):
                try:
                    title_element = element.find_element(By.CSS_SELECTOR, ".news_tit")
                    title = title_element.text.strip()
                    link = title_element.get_attribute("href")
                    
                    # 내용 추출 (있는 경우)
                    try:
                        content_element = element.find_element(By.CSS_SELECTOR, ".dsc_txt_wrap")
                        content = content_element.text.strip()
                    except:
                        content = ""
                    
                    # 날짜 추출 (있는 경우)
                    try:
                        date_element = element.find_element(By.CSS_SELECTOR, ".info_group .info")
                        date = date_element.text.strip()
                    except:
                        date = ""
                    
                    # 카테고리 추출 (있는 경우)
                    try:
                        category_element = element.find_element(By.CSS_SELECTOR, ".info_group .press")
                        category = category_element.text.strip()
                    except:
                        category = ""
                    
                    news_items.append({
                        "title": title,
                        "link": link,
                        "content": content,
                        "date": date,
                        "category": category
                    })
                    
                except Exception as e:
                    logger.warning(f"뉴스 항목 파싱 실패: {e}")
                    continue
            
            return news_items
            
        except Exception as e:
            logger.error(f"기업 뉴스 크롤링 실패: {e}")
            return []

    def crawl_analyst_reports(self, search_query: str, max_reports: int = 5) -> List[Dict]:
        """기업별 애널리스트 리포트 크롤링"""
        try:
            if not self.driver:
                self._init_driver()
            
            # 한국투자증권 리포트 검색 (예시)
            search_url = f"https://www.kiwoom.com/h/customer/guide/analyst/analystReport?searchKeyword={search_query}"
            self.driver.get(search_url)
            time.sleep(3)
            
            report_items = []
            
            # 리포트 목록 요소 찾기 (실제 사이트에 맞게 수정 필요)
            try:
                report_elements = self.driver.find_elements(By.CSS_SELECTOR, ".report-item")
                
                for i, element in enumerate(report_elements[:max_reports]):
                    try:
                        title_element = element.find_element(By.CSS_SELECTOR, ".title")
                        title = title_element.text.strip()
                        
                        # 애널리스트명 추출
                        try:
                            analyst_element = element.find_element(By.CSS_SELECTOR, ".analyst")
                            analyst = analyst_element.text.strip()
                        except:
                            analyst = "알 수 없음"
                        
                        # 요약 추출
                        try:
                            summary_element = element.find_element(By.CSS_SELECTOR, ".summary")
                            summary = summary_element.text.strip()
                        except:
                            summary = "요약 정보 없음"
                        
                        # 목표가 추출
                        try:
                            target_element = element.find_element(By.CSS_SELECTOR, ".target-price")
                            target_price = target_element.text.strip()
                        except:
                            target_price = "목표가 미정"
                        
                        # 날짜 추출
                        try:
                            date_element = element.find_element(By.CSS_SELECTOR, ".date")
                            date = date_element.text.strip()
                        except:
                            date = "날짜 정보 없음"
                        
                        report_items.append({
                            "title": title,
                            "analyst": analyst,
                            "summary": summary,
                            "target_price": target_price,
                            "date": date
                        })
                        
                    except Exception as e:
                        logger.warning(f"리포트 항목 파싱 실패: {e}")
                        continue
                        
            except Exception as e:
                logger.warning(f"리포트 목록 요소를 찾을 수 없음: {e}")
                # 폴백: 더미 데이터 반환
                report_items = [
                    {
                        "title": f"{search_query} 관련 리포트",
                        "analyst": "증권사 애널리스트",
                        "summary": "해당 기업에 대한 상세한 분석 리포트입니다.",
                        "target_price": "목표가 미정",
                        "date": "최근"
                    }
                ]
            
            return report_items
            
        except Exception as e:
            logger.error(f"애널리스트 리포트 크롤링 실패: {e}")
            return []


selenium_manager = SeleniumManager()