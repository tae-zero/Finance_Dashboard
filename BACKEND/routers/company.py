import pandas as pd
import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import json
from utils.selenium_utils import SeleniumManager
from services.company_service import CompanyService
from services.stock_service import StockService
from services.investor_service import InvestorService
from typing import List, Dict

router = APIRouter(prefix="/company", tags=["기업 정보"])

# 서비스 인스턴스
company_service = CompanyService()
stock_service = StockService()
investor_service = InvestorService()
selenium_manager = SeleniumManager()

# CSV 파일 경로
CSV_FILE_PATH = "NICE_내수수출_코스피.csv"

@router.get("/{name}")
async def get_company_data(name: str):
    """기업 데이터 조회"""
    try:
        company_data = company_service.get_company_data(name)
        if not company_data:
            raise HTTPException(status_code=404, detail="기업을 찾을 수 없습니다")
        return company_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"기업 데이터 조회 실패: {str(e)}")

@router.get("/names/all")
async def get_all_company_names():
    """전체 기업명 목록 조회"""
    try:
        # 임시로 빈 배열 반환 (나중에 구현)
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"기업 목록 조회 실패: {str(e)}")

@router.get("/metrics/{name}")
async def get_company_metrics(name: str):
    """기업 재무지표 조회"""
    try:
        # 임시로 빈 객체 반환 (나중에 구현)
        return {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"재무지표 조회 실패: {str(e)}")

@router.get("/sales/{name}")
async def get_company_sales(name: str):
    """기업 매출 데이터 조회"""
    try:
        # 임시로 빈 객체 반환 (나중에 구현)
        return {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"매출 데이터 조회 실패: {str(e)}")

@router.get("/treasure/data")
async def get_treasure_data():
    """투자 보물찾기 데이터 조회"""
    try:
        # 임시로 빈 객체 반환 (나중에 구현)
        return {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"보물찾기 데이터 조회 실패: {str(e)}")

@router.get("/data/financial-metrics")
async def get_financial_metrics():
    """기업별 재무지표 JSON 데이터"""
    try:
        with open("기업별_재무지표.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="재무지표 파일을 찾을 수 없습니다")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"재무지표 데이터 로드 실패: {str(e)}")

@router.get("/data/industry-metrics")
async def get_industry_metrics():
    """산업별 지표 JSON 데이터"""
    try:
        with open("industry_metrics.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="산업지표 파일을 찾을 수 없습니다")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"산업지표 데이터 로드 실패: {str(e)}")

@router.get("/data/sales-data")
async def get_sales_data():
    """매출비중 차트 데이터 JSON"""
    try:
        with open("매출비중_chartjs_데이터.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="매출데이터 파일을 찾을 수 없습니다")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"매출데이터 로드 실패: {str(e)}")

@router.get("/data/shareholder-data")
async def get_shareholder_data():
    """지분현황 JSON 데이터"""
    try:
        with open("지분현황.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="지분현황 파일을 찾을 수 없습니다")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"지분현황 데이터 로드 실패: {str(e)}")

@router.get("/company/{company_name}")
async def get_company_info(company_name: str):
    """기업 정보 조회"""
    try:
        company_data = company_service.get_company_data(company_name)
        if not company_data:
            raise HTTPException(status_code=404, detail="기업을 찾을 수 없습니다.")
        return company_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"기업 정보 조회 실패: {str(e)}")

@router.get("/company/{company_name}/sales-composition")
async def get_company_sales_composition(company_name: str):
    """기업별 매출 구성 데이터 조회 (CSV 파일에서)"""
    try:
        if not os.path.exists(CSV_FILE_PATH):
            raise HTTPException(status_code=404, detail="매출 구성 데이터 파일을 찾을 수 없습니다.")
        
        # CSV 파일 읽기
        df = pd.read_csv(CSV_FILE_PATH, encoding='utf-8')
        
        # 종목명으로 데이터 찾기
        company_data = df[df['종목명'] == company_name]
        
        if company_data.empty:
            # 정확한 매칭이 안되면 부분 매칭 시도
            company_data = df[df['종목명'].str.contains(company_name, na=False)]
        
        if company_data.empty:
            return {"message": "해당 기업의 매출 구성 데이터를 찾을 수 없습니다.", "data": None}
        
        # 첫 번째 매칭 결과 반환
        result = company_data.iloc[0].to_dict()
        
        return {
            "message": "매출 구성 데이터 조회 성공",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"매출 구성 데이터 조회 실패: {str(e)}")

@router.get("/company/{company_name}/news")
async def get_company_news(company_name: str):
    """기업 관련 뉴스 크롤링"""
    try:
        news_data = await selenium_manager.crawl_company_news(company_name)
        return {"news": news_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"뉴스 크롤링 실패: {str(e)}")

@router.get("/company/{company_name}/analyst-report")
async def get_analyst_report(company_name: str):
    """애널리스트 리포트 크롤링"""
    try:
        # 기업 정보에서 종목코드 가져오기
        company_data = company_service.get_company_data(company_name)
        if not company_data:
            raise HTTPException(status_code=404, detail="기업을 찾을 수 없습니다.")
        
        종목코드 = company_data.get('종목코드')
        if not 종목코드:
            raise HTTPException(status_code=400, detail="종목코드 정보가 없습니다.")
        
        # fnguide.com에서 직접 크롤링
        url = f"https://www.fnguide.com/SPV/SPV_1000.asp?gnb=1&gno={종목코드}"
        
        # 사용자 제공 로직 사용
        def custom_scraping_logic(driver):
            try:
                # 페이지 로드 대기
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
                from selenium.webdriver.common.by import By
                
                wait = WebDriverWait(driver, 10)
                
                # 애널리스트 리포트 테이블 찾기
                table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.table_common")))
                
                # 테이블 데이터 파싱
                rows = table.find_elements(By.CSS_SELECTOR, "tr")
                reports = []
                
                for row in rows[1:]:  # 헤더 제외
                    try:
                        cells = row.find_elements(By.CSS_SELECTOR, "td")
                        if len(cells) >= 4:
                            date = cells[0].text.strip()
                            title = cells[1].text.strip()
                            analyst = cells[2].text.strip()
                            target_price = cells[3].text.strip()
                            
                            if date and title:  # 유효한 데이터만
                                reports.append({
                                    "date": date,
                                    "title": title,
                                    "analyst": analyst,
                                    "target_price": target_price,
                                    "summary": f"{title} - {analyst} 분석"
                                })
                    except Exception as e:
                        continue
                
                return {"reports": reports}
                
            except Exception as e:
                return {"reports": [], "error": str(e)}
        
        # Selenium으로 크롤링 실행
        result = await selenium_manager.scrape_with_custom_logic(url, custom_scraping_logic)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"애널리스트 리포트 크롤링 실패: {str(e)}")
