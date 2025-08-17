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
            url = 'https://search.daum.net/nate?w=news&nil_search=btn&DA=PGD&enc=utf8&cluster=y&cluster_page=1&q=코스피'
            selector = '#dnsColl > div:nth-child(1) > ul > li > div.c-item-content > div > div.item-title > strong > a'
            
            return await selenium_manager.scrape_news(url, selector, max_items=5)
            
        except Exception as e:
            print(f"❌ 코스피 뉴스 조회 실패: {e}")
            return []
    
    async def get_earnings_news(self) -> List[Dict]:
        """실적 발표 관련 뉴스 조회"""
        try:
            url = 'https://search.daum.net/nate?w=news&nil_search=btn&DA=PGD&enc=utf8&cluster=y&cluster_page=1&q=실적 발표'
            selector = '#dnsColl > div:nth-child(1) > ul > li > div.c-item-content > div > div.item-title > strong > a'
            
            return await selenium_manager.scrape_news(url, selector, max_items=5)
            
        except Exception as e:
            print(f"❌ 실적 뉴스 조회 실패: {e}")
            return []
    
    async def search_company_news(self, keyword: str) -> List[Dict]:
        """기업별 키워드 뉴스 검색"""
        try:
            # 네이버 뉴스로 변경
            url = f'https://search.naver.com/search.naver?where=news&query={keyword}&sort=1'
            selector = 'a.news_tit'
            
            # 대기 시간 증가 및 최대 아이템 수 조정
            return await selenium_manager.scrape_news(url, selector, max_items=10, wait_time=5)
            
        except Exception as e:
            logger.error(f"❌ 기업 뉴스 조회 실패: {e}")
            # 실패 시 더미 데이터 반환
            return [{
                "title": f"{keyword} 관련 뉴스",
                "url": "https://search.naver.com/search.naver?where=news",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }]
    
    async def get_analyst_reports(self, code: str) -> List[Dict]:
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
            
            return await selenium_manager.scrape_with_custom_logic(url, custom_scraping_logic, wait_time=2)
            
        except Exception as e:
            print(f"❌ 애널리스트 리포트 조회 실패: {e}")
            return []
    
    def _extract_text_safely(self, element, xpath: str, default: str = "") -> str:
        """안전한 텍스트 추출"""
        try:
            from selenium.webdriver.common.by import By
            text = element.find_element(By.XPATH, xpath).text.strip()
            return text if text else default
        except:
            return default
    
    def safe_get(self, data, key, default=""):
        """안전한 데이터 추출"""
        try:
            return data.get(key, default)
        except:
            return default
