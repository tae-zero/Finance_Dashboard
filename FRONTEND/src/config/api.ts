import axios from 'axios';

// API 기본 설정
const API_BASE_URL = '/api/v1';  // 상대 경로 사용

// Axios 인스턴스 생성
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// 응답 인터셉터
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    console.error('API 오류:', error);
    
    if (error.response?.status === 503) {
      console.warn('외부 서비스 일시적 오류');
    }
    
    return Promise.reject(error);
  }
);

// 요청 인터셉터
api.interceptors.request.use(
  (config) => {
    // 요청 설정 수정
    config.headers['X-Requested-With'] = 'XMLHttpRequest';
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export const API_ENDPOINTS = {
  // 기업 관련
  COMPANY: (name: string) => `/company/${encodeURIComponent(name)}`,
  COMPANY_NAMES: `/company/names/all`,
  COMPANY_METRICS: (name: string) => `/company/metrics/${encodeURIComponent(name)}`,
  COMPANY_SALES: (name: string) => `/company/sales/${encodeURIComponent(name)}`,
  
  // 뉴스 관련
  HOT_NEWS: `/news/hot/kospi`,
  MAIN_NEWS: `/news/earnings`,
  COMPANY_NEWS: (keyword: string) => `/news/search?keyword=${encodeURIComponent(keyword)}`,
  ANALYST_REPORT: (code: string) => `/news/analyst/report?code=${code}`,
  
  // 주가 관련
  STOCK_PRICE: (ticker: string) => `/stock/price/${ticker}`,
  KOSPI_DATA: `/stock/kospi/index`,
  MARKET_CAP_TOP10: `/stock/marketcap/top10`,
  TOP_VOLUME: `/stock/volume/top5`,
  INDUSTRY_ANALYSIS: (name: string) => `/stock/industry/${encodeURIComponent(name)}`,
  
  // 투자자 관련
  INVESTOR_VALUE: `/investor/value`,
  INVESTOR_SUMMARY: (ticker: string) => `/investor/summary/${ticker}`,
  INVESTOR_TRENDS: (days: number) => `/investor/trends?days=${days}`,
  
  // 기타
  TREASURE_DATA: `/company/treasure/data`,
  TOP_RANKINGS: `/investor/rankings/top5`,
};

export default api;