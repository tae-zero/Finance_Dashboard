import axios, { AxiosError } from 'axios';

// 브라우저에서는 무조건 상대 경로 사용 (환경변수 무시)
const API_BASE_URL = '/api/v1';

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
  COMPANY: (name: string) => `/company/${encodeURIComponent(name)}`,
  COMPANY_NAMES: `/company/names/all`,
  COMPANY_METRICS: (name: string) => `/company/metrics/${encodeURIComponent(name)}`,
  COMPANY_SALES: (name: string) => `/company/sales/${encodeURIComponent(name)}`,
  HOT_NEWS: `/news/hot/kospi`,
  MAIN_NEWS: `/news/earnings`,
  COMPANY_NEWS: (keyword: string) => `/news/search?keyword=${encodeURIComponent(keyword)}`,
  ANALYST_REPORT: (code: string) => `/news/analyst/report?code=${code}`,
  STOCK_PRICE: (ticker: string) => `/stock/price/${ticker}`,
  KOSPI_DATA: `/stock/kospi/index`,
  MARKET_CAP_TOP10: `/stock/marketcap/top10`,
  TOP_VOLUME: `/stock/volume/top5`,
  INDUSTRY_ANALYSIS: (name: string) => `/stock/industry/${encodeURIComponent(name)}`,
  INVESTOR_VALUE: `/investor/value`,
  INVESTOR_SUMMARY: (ticker: string) => `/investor/summary/${ticker}`,
  INVESTOR_TRENDS: (days: number) => `/investor/trends?days=${days}`,
  TREASURE_DATA: `/company/treasure/data`,
  TOP_RANKINGS: `/investor/rankings/top5`,
  
  // JSON 데이터 API 엔드포인트 추가
  FINANCIAL_METRICS: `/company/data/financial-metrics`,
  INDUSTRY_METRICS: `/company/data/industry-metrics`,
  SALES_DATA: `/company/data/sales-data`,
  SHAREHOLDER_DATA: `/company/data/shareholder-data`,
};

// 디버깅 로그
console.log('[api] API_BASE_URL (강제 설정):', API_BASE_URL);
console.log('[api] API 객체 생성됨:', api);
console.log('[api] API 객체 타입:', typeof api);
console.log('[api] API 객체의 get 메서드:', api.get);
console.log('[api] API_ENDPOINTS 생성됨:', API_ENDPOINTS);

export default api;
