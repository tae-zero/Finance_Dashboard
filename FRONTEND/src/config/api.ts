import axios, { AxiosError } from 'axios';

// 로컬 개발 환경에서는 백엔드 서버 직접 연결
const API_BASE_URL = 'http://localhost:7000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

// 타입 경고 방지 + 기본 헤더 설정
api.defaults.headers.post['Content-Type']  = 'application/json';
api.defaults.headers.put['Content-Type']   = 'application/json';
api.defaults.headers.patch['Content-Type'] = 'application/json';
api.defaults.headers.delete['Content-Type']= 'application/json';

api.interceptors.request.use((config) => {
  config.headers = config.headers || {};
  (config.headers as any)['X-Requested-With'] = 'XMLHttpRequest';
  
  // 디버깅: 요청 URL 로깅
  const baseURL = config.baseURL || '';
  const url = config.url || '';
  console.log('[api] 요청 URL:', baseURL + url);
  
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err: AxiosError<any>) => {
    const status = err.response?.status;
    const data = err.response?.data;
    console.error('API 오류:', { 
      url: err.config?.url, 
      method: err.config?.method, 
      status, 
      data 
    });
    
    if (status === 503) {
      console.warn('외부 서비스 일시적 오류');
    }
    
    return Promise.reject(err);
  }
);

export const API_ENDPOINTS = {
  // 기존 엔드포인트들
  COMPANY: (name: string) => `/company/${encodeURIComponent(name)}`,
  STOCK_PRICE: (ticker: string) => `/stock/price/${ticker}`,
  INVESTOR_SUMMARY: (code: string) => `/investor/summary/${code}`,
  
  // 새로운 엔드포인트들
  COMPANY_NEWS: (name: string) => `/company/${encodeURIComponent(name)}/news`,
  ANALYST_REPORT: (name: string) => `/company/${encodeURIComponent(name)}/analyst-report`,
  COMPANY_NAMES: '/company/names/all',  // 기업 목록 조회 엔드포인트
  
  // JSON 데이터 엔드포인트들
  FINANCIAL_METRICS: '/company/data/financial-metrics',
  INDUSTRY_METRICS: '/company/data/industry-metrics',
  SALES_DATA: '/company/data/sales-data',
  SHAREHOLDER_DATA: '/company/data/shareholder-data',
  
  // 대시보드 엔드포인트들
  HOT_NEWS: '/news/hot/kospi',
  MAIN_NEWS: '/news/earnings',
  KOSPI_DATA: '/stock/price/^KS11',
  INVESTOR_VALUE: '/investor/value',
  
  // 랭킹 엔드포인트들
  TOP_RANKINGS: '/stock/market-cap-top10',      // 시가총액 TOP 10
  MARKET_CAP_TOP10: '/stock/market-cap-top10',  // 시가총액 TOP 10 (별칭)
  TOP_VOLUME: '/stock/top-volume',              // 거래량 TOP 5
  
  // 보물찾기 엔드포인트
  TREASURE_DATA: '/company/treasure/data',       // 보물찾기 데이터
};

// 디버깅 로그
console.log('[api] API_BASE_URL (강제 설정):', API_BASE_URL);
console.log('[api] API 객체 생성됨:', api);
console.log('[api] API 객체 타입:', typeof api);
console.log('[api] API 객체의 get 메서드:', api.get);
console.log('[api] API_ENDPOINTS 생성됨:', API_ENDPOINTS);

export default api;
