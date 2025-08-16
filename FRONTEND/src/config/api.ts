import axios from 'axios';

const API_BASE_URL = '/api';   // Vercel rewrites 통로
const API_PREFIX   = '/v1';    // 버전 별도 관리

// axios 인스턴스 생성
const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

// API 객체를 직접 axios 인스턴스로 export
const api = axiosInstance;

// 엔드포인트
export const API_ENDPOINTS = {
  // 기업
  COMPANY: (name: string) => `${API_PREFIX}/company/${encodeURIComponent(name)}`,
  COMPANY_NAMES:           `${API_PREFIX}/company/names/all`,
  COMPANY_METRICS: (name: string) => `${API_PREFIX}/company/metrics/${encodeURIComponent(name)}`,
  COMPANY_SALES:   (name: string) => `${API_PREFIX}/company/sales/${encodeURIComponent(name)}`,

  // 뉴스
  HOT_NEWS:        `${API_PREFIX}/news/hot/kospi`,
  MAIN_NEWS:       `${API_PREFIX}/news/earnings`,
  COMPANY_NEWS: (keyword: string) => `${API_PREFIX}/news/search?keyword=${encodeURIComponent(keyword)}`,
  ANALYST_REPORT: (code: string) => `${API_PREFIX}/news/analyst/report?code=${encodeURIComponent(code)}`,

  // 주가
  STOCK_PRICE:   (ticker: string) => `${API_PREFIX}/stock/price/${encodeURIComponent(ticker)}`,
  KOSPI_DATA:                      `${API_PREFIX}/stock/kospi/index`,
  MARKET_CAP_TOP10:                `${API_PREFIX}/stock/marketcap/top10`,
  TOP_VOLUME:                      `${API_PREFIX}/stock/volume/top5`,
  INDUSTRY_ANALYSIS: (name: string) => `${API_PREFIX}/stock/industry/${encodeURIComponent(name)}`,

  // 투자자
  INVESTOR_VALUE:                 `${API_PREFIX}/investor/value`,
  INVESTOR_SUMMARY: (ticker: string) => `${API_PREFIX}/investor/summary/${encodeURIComponent(ticker)}`,
  INVESTOR_TRENDS:  (days: number)   => `${API_PREFIX}/investor/trends?days=${days}`,

  // 기타
  TREASURE_DATA:                  `${API_PREFIX}/company/treasure/data`,
  TOP_RANKINGS:                   `${API_PREFIX}/investor/rankings/top5`,
};

// 디버깅을 위한 로그
console.log('[api] API 객체 생성됨:', api);
console.log('[api] API_ENDPOINTS 생성됨:', API_ENDPOINTS);

export default api;
