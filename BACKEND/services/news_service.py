from utils.selenium_utils import selenium_manager
from fastapi import HTTPException
from typing import List, Dict

class NewsService:
    def __init__(self):
        # 전역 selenium_manager 인스턴스 사용
        pass
    
    async def get_kospi_news(self) -> List[Dict]:
        """코스피 관련 뉴스 조회"""
        try:
            url = "https://finance.naver.com/sise/sise_index.naver?code=KOSPI"
            selector = ".news_list a"
            news_data = await selenium_manager.scrape_news(url, selector, max_items=10)
            return news_data
        except Exception as e:
            print(f"❌ 뉴스 조회 실패: {e}")
            # 오류 시 빈 배열 반환
            return []
    
    async def get_earnings_news(self) -> List[Dict]:
        """실적 발표 관련 뉴스 조회"""
        try:
            url = "https://finance.naver.com/news/news_list.naver?type=earnings"
            selector = ".news_list a"
            news_data = await selenium_manager.scrape_news(url, selector, max_items=10)
            return news_data
        except Exception as e:
            print(f"❌ 실적 뉴스 조회 실패: {e}")
            return []
    
    async def search_company_news(self, keyword: str) -> List[Dict]:
        """특정 기업 관련 뉴스 조회"""
        try:
            url = f"https://finance.naver.com/search/search.naver?query={keyword}"
            selector = ".article_list a"
            news_data = await selenium_manager.scrape_news(url, selector, max_items=10)
            return news_data
        except Exception as e:
            print(f"❌ 기업 뉴스 조회 실패: {e}")
            return []
    
    async def get_analyst_reports(self, code: str) -> List[Dict]:
        """종목분석 리포트 조회"""
        try:
            url = f"https://finance.naver.com/research/analyst_list.naver?code={code}"
            selector = ".analyst_list a"
            news_data = await selenium_manager.scrape_news(url, selector, max_items=10)
            return news_data
        except Exception as e:
            print(f"❌ 애널리스트 리포트 조회 실패: {e}")
            return []
    
    def safe_get(self, data, key, default=""):
        """안전한 데이터 추출"""
        try:
            return data.get(key, default)
        except:
            return default
