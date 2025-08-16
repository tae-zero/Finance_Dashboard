import axios, { AxiosError } from 'axios';

const isBrowser = typeof window !== 'undefined';

// 브라우저: 반드시 리라이트 타게 함 → 상대 경로 고정
// 서버(SSR)에서만 절대 URL 허용(필요할 때). 서버용 env는 NEXT_PUBLIC 금지.
const API_BASE_URL =
  isBrowser
    ? '/api/v1'
    : (process.env.API_BASE_URL?.replace(/\/$/, '') || 'http://127.0.0.1:7000') + '/api/v1';

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
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err: AxiosError) => {
    console.error('API 오류:', err);
    if (err.response?.status === 503) console.warn('외부 서비스 일시적 오류');
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
};

// 디버깅 로그
console.log('[api] API_BASE_URL:', API_BASE_URL);
console.log('[api] isBrowser:', isBrowser);
console.log('[api] API 객체 생성됨:', api);
console.log('[api] API_ENDPOINTS 생성됨:', API_ENDPOINTS);

export default api;
