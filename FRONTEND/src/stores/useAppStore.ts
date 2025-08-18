import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AppState {
  // 사용자 설정
  theme: 'light' | 'dark';
  language: 'ko' | 'en';
  
  // API 상태
  isLoading: boolean;
  error: string | null;
  
  // 데이터 상태
  companyData: any;
  newsData: any;
  stockData: any;
  
  // 액션들
  setTheme: (theme: 'light' | 'dark') => void;
  setLanguage: (language: 'ko' | 'en') => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setCompanyData: (data: any) => void;
  setNewsData: (data: any) => void;
  setStockData: (data: any) => void;
  resetStore: () => void;
}

const initialState = {
  theme: 'light' as const,
  language: 'ko' as const,
  isLoading: false,
  error: null,
  companyData: null,
  newsData: null,
  stockData: null,
};

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      ...initialState,
      
      setTheme: (theme) => set({ theme }),
      setLanguage: (language) => set({ language }),
      setLoading: (isLoading) => set({ isLoading }),
      setError: (error) => set({ error }),
      setCompanyData: (companyData) => set({ companyData }),
      setNewsData: (newsData) => set({ newsData }),
      setStockData: (stockData) => set({ stockData }),
      
      resetStore: () => set(initialState),
    }),
    {
      name: 'finance-dashboard-storage',
      partialize: (state) => ({
        theme: state.theme,
        language: state.language,
      }),
    }
  )
);
