import axios from 'axios';

// axios 인스턴스 생성
const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
});

// 엔드포인트 정의
export const API_ENDPOINTS = {
  // 기업
  COMPANY: (name: string) => `/v1/company/${encodeURIComponent(name)}`,
  COMPANY_NAMES: `/v1/company/names/all`,
  COMPANY_METRICS: (name: string) => `/v1/company/metrics/${encodeURIComponent(name)}`,
  COMPANY_SALES: (name: string) => `/v1/company/sales/${encodeURIComponent(name)}`,

  // 뉴스
  HOT_NEWS: `/v1/news/hot/kospi`,
  MAIN_NEWS: `/v1/news/earnings`,
  COMPANY_NEWS: (keyword: string) => `/v1/news/search?keyword=${encodeURIComponent(keyword)}`,
  ANALYST_REPORT: (code: string) => `/v1/news/analyst/report?code=${encodeURIComponent(code)}`,

  // 주가
  STOCK_PRICE: (ticker: string) => `/v1/stock/price/${encodeURIComponent(ticker)}`,
  KOSPI_DATA: `/v1/stock/kospi/index`,
  MARKET_CAP_TOP10: `/v1/stock/marketcap/top10`,
  TOP_VOLUME: `/v1/stock/volume/top5`,
  INDUSTRY_ANALYSIS: (name: string) => `/v1/stock/industry/${encodeURIComponent(name)}`,

  // 투자자
  INVESTOR_VALUE: `/v1/investor/value`,
  INVESTOR_SUMMARY: (ticker: string) => `/v1/investor/summary/${encodeURIComponent(ticker)}`,
  INVESTOR_TRENDS: (days: number) => `/v1/investor/trends?days=${days}`,

  // 기타
  TREASURE_DATA: `/v1/company/treasure/data`,
  TOP_RANKINGS: `/v1/investor/rankings/top5`,
};

// 디버깅 로그
console.log('[api] API 객체 생성됨:', api);
console.log('[api] API_ENDPOINTS 생성됨:', API_ENDPOINTS);

export default api;
