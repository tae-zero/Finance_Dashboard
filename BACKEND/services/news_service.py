from utils.selenium_utils import SeleniumManager
from fastapi import HTTPException
from typing import List, Dict

class NewsService:
    def __init__(self):
        self.selenium_manager = SeleniumManager()
    
    def get_kospi_news(self) -> List[Dict]:
        """코스피 관련 뉴스 조회"""
        try:
            url = 'https://search.daum.net/nate?w=news&nil_search=btn&DA=PGD&enc=utf8&cluster=y&cluster_page=1&q=코스피'
            selector = '#dnsColl > div:nth-child(1) > ul > li > div.c-item-content > div > div.item-title > strong > a'
            
            return self.selenium_manager.scrape_news(url, selector, max_items=5)
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"코스피 뉴스 조회 중 오류: {str(e)}")
    
    def get_earnings_news(self) -> List[Dict]:
        """실적 발표 관련 뉴스 조회"""
        try:
            url = 'https://search.daum.net/nate?w=news&nil_search=btn&DA=PGD&enc=utf8&cluster=y&cluster_page=1&q=실적 발표'
            selector = '#dnsColl > div:nth-child(1) > ul > li > div.c-item-content > div > div.item-title > strong > a'
            
            return self.selenium_manager.scrape_news(url, selector, max_items=5)
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"실적 발표 뉴스 조회 중 오류: {str(e)}")
    
    def search_company_news(self, keyword: str) -> List[Dict]:
        """기업별 키워드 뉴스 검색"""
        try:
            url = f'https://search.daum.net/nate?w=news&nil_search=btn&DA=PGD&enc=utf8&cluster=y&cluster_page=1&q={keyword}'
            selector = '#dnsColl > div:nth-child(1) > ul > li > div.c-item-content > div > div.item-title > strong > a'
            
            return self.selenium_manager.scrape_news(url, selector, max_items=10, wait_time=2)
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"'{keyword}' 뉴스 검색 중 오류: {str(e)}")
    
    def get_analyst_reports(self, code: str) -> List[Dict]:
        """종목분석 리포트 조회"""
        try:
            url = f"https://comp.fnguide.com/SVO2/ASP/SVD_Consensus.asp?pGB=1&gicode={code}&MenuYn=Y&ReportGB=&NewMenuID=108"
            
            def custom_scraping_logic(driver):
                from selenium.webdriver.common.by import By
                
                data = []
                try:
                    rows = driver.find_elements(By.XPATH, '//*[@id="bodycontent4"]/tr')
                    
                    for row in rows:
                        try:
                            # 각 컬럼 데이터 추출
                            date = row.find_element(By.XPATH, './td[1]').text.strip()
                            title = row.find_element(By.XPATH, './td[2]//span[@class="txt2"]').text.strip()
                            
                            # 요약 정보 추출
                            summary_parts = row.find_elements(By.XPATH, './td[2]//dd')
                            summary = " / ".join([p.text.strip() for p in summary_parts if p.text.strip()])
                            
                            # 추가 정보 추출
                            opinion = self._extract_text_safely(row, './td[3]/span', '')
                            target_price = self._extract_text_safely(row, './td[4]/span', '')
                            closing_price = self._extract_text_safely(row, './td[5]', '')
                            analyst = self._extract_text_safely(row, './td[6]', '')
                            
                            data.append({
                                "date": date,
                                "title": title,
                                "summary": summary,
                                "opinion": opinion,
                                "target_price": target_price,
                                "closing_price": closing_price,
                                "analyst": analyst
                            })
                            
                            if len(data) >= 5:
                                break
                                
                        except Exception as e:
                            print(f"⚠️ 행 파싱 중 오류 발생: {e}")
                            continue
                            
                except Exception as e:
                    print(f"⚠️ 전체 파싱 중 오류 발생: {e}")
                
                return data
            
            return self.selenium_manager.scrape_with_custom_logic(url, custom_scraping_logic, wait_time=2)
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"분석 리포트 조회 중 오류: {str(e)}")
    
    def _extract_text_safely(self, element, xpath: str, default: str = "") -> str:
        """안전한 텍스트 추출"""
        try:
            text = element.find_element(By.XPATH, xpath).text.strip()
            return text if text else default
        except:
            return default
