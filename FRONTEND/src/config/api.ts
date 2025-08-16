import axios, { AxiosRequestConfig } from 'axios';

const API_BASE_URL = '/api';   // Vercel rewrites 통로
const API_PREFIX   = '/v1';    // 버전 별도 관리

// axios 인스턴스 생성
const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  // 전역 headers는 최소화 (프리플라이트 줄이기)
});

// 절대 URL이면 상대 URL로 강제 변환 (브라우저에서만)
function toRelativeIfAbsolute(config: AxiosRequestConfig) {
  const u = config.url || '';
  if (typeof window !== 'undefined' && /^https?:\/\//i.test(u)) {
    try {
      const parsed = new URL(u);
      config.url = parsed.pathname + parsed.search; // /api/... 형태만 남김
      config.baseURL = API_BASE_URL;
      console.warn('[api] Rewrote absolute URL to relative:', config.url);
    } catch {
      // ignore
    }
  }
}

axiosInstance.interceptors.request.use(
  (config) => {
    toRelativeIfAbsolute(config);

    const method = (config.method || 'get').toLowerCase();
    const hasBody = ['post', 'put', 'patch', 'delete'].includes(method) && config.data != null;

    // 바디가 있는 요청에만 Content-Type 지정
    if (hasBody) {
      if (!config.headers) {
        config.headers = {} as any;
      }
      config.headers['Content-Type'] = 'application/json';
    }
    // 커스텀 헤더(X-Requested-With 등) 추가 금지

    return config;
  },
  (error) => Promise.reject(error)
);

axiosInstance.interceptors.response.use(
  (res) => res,
  (error) => {
    console.error('API 오류:', error);
    if (error?.response?.status === 503) {
      console.warn('외부 서비스 일시적 오류');
    }
    return Promise.reject(error);
  }
);

// API 객체 정의
const api = {
  get: (url: string, config?: any) => {
    console.log('[api] GET 요청:', url);
    return axiosInstance.get(url, config);
  },
  post: (url: string, data?: any, config?: any) => {
    console.log('[api] POST 요청:', url);
    return axiosInstance.post(url, data, config);
  },
  put: (url: string, data?: any, config?: any) => {
    console.log('[api] PUT 요청:', url);
    return axiosInstance.put(url, data, config);
  },
  delete: (url: string, config?: any) => {
    console.log('[api] DELETE 요청:', url);
    return axiosInstance.delete(url, config);
  },
  patch: (url: string, data?: any, config?: any) => {
    console.log('[api] PATCH 요청:', url);
    return axiosInstance.patch(url, data, config);
  }
};

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
