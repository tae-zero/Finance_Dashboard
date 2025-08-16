from utils.selenium_utils import SeleniumManager
from fastapi import HTTPException
from typing import List, Dict

class NewsService:
    def __init__(self):
        self.selenium_manager = SeleniumManager()
    
    def get_kospi_news(self) -> List[Dict]:
        """코스피 관련 뉴스 조회"""
        try:
            url = "https://finance.naver.com/sise/sise_index.naver?code=KOSPI"
            selector = ".news_list a"
            news_data = self.selenium_manager.scrape_news(url, selector, max_items=10)
            return news_data
        except Exception as e:
            print(f"❌ 뉴스 조회 실패: {e}")
            return []
    
    def get_company_news(self, company_name: str) -> List[Dict]:
        """특정 기업 관련 뉴스 조회"""
        try:
            url = f"https://finance.naver.com/search/search.naver?query={company_name}"
            selector = ".article_list a"
            news_data = self.selenium_manager.scrape_news(url, selector, max_items=10)
            return news_data
        except Exception as e:
            print(f"❌ 기업 뉴스 조회 실패: {e}")
            return []
    
    def safe_get(self, data, key, default=""):
        """안전한 데이터 추출"""
        try:
            return data.get(key, default)
        except:
            return default
