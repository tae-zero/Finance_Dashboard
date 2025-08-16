// API 설정
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://financedashboard-production-50f3.up.railway.app';

export const API_ENDPOINTS = {
  // 기업 관련
  COMPANY: (name: string) => `${API_BASE_URL}/api/v1/company/${encodeURIComponent(name)}`,
  COMPANY_NAMES: `${API_BASE_URL}/api/v1/company/names/all`,
  COMPANY_METRICS: (name: string) => `${API_BASE_URL}/api/v1/company/metrics/${encodeURIComponent(name)}`,
  COMPANY_SALES: (name: string) => `${API_BASE_URL}/api/v1/company/sales/${encodeURIComponent(name)}`,
  
  // 뉴스 관련
  HOT_NEWS: `${API_BASE_URL}/api/v1/news/hot/kospi`,
  MAIN_NEWS: `${API_BASE_URL}/api/v1/news/earnings`,
  COMPANY_NEWS: (keyword: string) => `${API_BASE_URL}/api/v1/news/search?keyword=${encodeURIComponent(keyword)}`,
  ANALYST_REPORT: (code: string) => `${API_BASE_URL}/api/v1/news/analyst/report?code=${code}`,
  
  // 주가 관련
  STOCK_PRICE: (ticker: string) => `${API_BASE_URL}/api/v1/stock/price/${ticker}`,
  KOSPI_DATA: `${API_BASE_URL}/api/v1/stock/kospi/index`,
  MARKET_CAP_TOP10: `${API_BASE_URL}/api/v1/stock/marketcap/top10`,
  TOP_VOLUME: `${API_BASE_URL}/api/v1/stock/volume/top5`,
  INDUSTRY_ANALYSIS: (name: string) => `${API_BASE_URL}/api/v1/stock/industry/${encodeURIComponent(name)}`,
  
  // 투자자 관련
  INVESTOR_VALUE: `${API_BASE_URL}/api/v1/investor/value`,
  INVESTOR_SUMMARY: (ticker: string) => `${API_BASE_URL}/api/v1/investor/summary/${ticker}`,
  INVESTOR_TRENDS: (days: number) => `${API_BASE_URL}/api/v1/investor/trends?days=${days}`,
  
  // 기타
  TREASURE_DATA: `${API_BASE_URL}/api/v1/company/treasure/data`,
  
  // 추가 엔드포인트들
  TOP_RANKINGS: `${API_BASE_URL}/api/v1/investor/rankings/top5`,
};

export default API_BASE_URL;

