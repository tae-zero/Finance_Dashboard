'use client'

import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import TopRankings from './TopRankings';
import api, { API_ENDPOINTS } from '../config/api';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface NewsItem {
  id: number;
  title: string;
  content: string;
  date: string;
  category: string;
}

interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    borderColor: string;
    backgroundColor: string;
    tension: number;
    pointRadius: number;
    borderWidth: number;
  }[];
}

function Dashboard() {
  const [hotNews, setHotNews] = useState<NewsItem[]>([]);
  const [mainNews, setMainNews] = useState<NewsItem[]>([]);
  const [chartData, setChartData] = useState<ChartData | null>(null);
  const [investorData, setInvestorData] = useState<any[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      // API 객체 확인
      console.log("🔍 API 객체 확인:", api);
      console.log("🔍 API_ENDPOINTS 확인:", API_ENDPOINTS);
      
      if (!api || typeof api.get !== 'function') {
        console.error("❌ API 객체가 올바르게 로드되지 않았습니다:", api);
        return;
      }

      try {
        console.log("🔥 핫 뉴스 API 호출 중...");
        const hotRes = await api.get(API_ENDPOINTS.HOT_NEWS);
        console.log("✅ 핫 뉴스 성공:", hotRes.data);
        setHotNews(hotRes.data);
      } catch (err) {
        console.error("❌ 핫 뉴스 오류:", err);
      }

      try {
        console.log("📰 실적 뉴스 API 호출 중...");
        const mainRes = await api.get(API_ENDPOINTS.MAIN_NEWS);
        console.log("✅ 실적 뉴스 성공:", mainRes.data);
        setMainNews(mainRes.data);
      } catch (err) {
        console.error("❌ 실적 뉴스 오류:", err);
      }

      try {
        console.log("📈 코스피 데이터 API 호출 중...");
        const kospiRes = await api.get(API_ENDPOINTS.KOSPI_DATA);
        console.log("✅ 코스피 데이터 성공:", kospiRes.data);
      
        const data = kospiRes.data;
        if (!Array.isArray(data) || data.length === 0) {
          console.warn("⚠️ KOSPI 데이터 없음");
          return;
        }
        const labels = data.map((item: any) => item.Date);
        const closes = data.map((item: any) => parseFloat(item.Close));
        setChartData({
          labels,
          datasets: [
            {
              label: 'KOSPI 종가',
              data: closes,
              borderColor: '#3b82f6',
              backgroundColor: 'rgba(59, 130, 246, 0.1)',
              tension: 0.3,
              pointRadius: 0,
              borderWidth: 3,
            },
          ],
        });
      } catch (err) {
        console.error("❌ 코스피 데이터 오류:", err);
      }

      try {
        console.log("💰 투자자별 매매 동향 API 호출 중...");
        const investorRes = await api.get(API_ENDPOINTS.INVESTOR_VALUE);
        console.log("✅ 투자자별 매매 동향 성공:", investorRes.data);
        setInvestorData(investorRes.data);
      } catch (err) {
        console.error("❌ 투자자별 매매 동향 오류:", err);
      }
    };

    fetchData();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 p-6">
      <div className="max-w-full mx-auto">
        {/* 헤더 */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-24 h-24 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-full mb-8 shadow-2xl">
            <span className="text-4xl">🎯</span>
          </div>
          <h1 className="text-5xl md:text-6xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-6">
            주린이 놀이터
          </h1>
          <p className="text-2xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
            주린이를 위한 친절한 주식투자 대시보드
          </p>
        </div>

        {/* 상단: 뉴스 섹션 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* 핫뉴스 */}
          <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-lg">
            <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-3">
              <span className="text-2xl">🔥</span>
              핫뉴스
            </h2>
            <div className="space-y-4">
              {hotNews.length > 0 ? (
                hotNews.slice(0, 5).map((news, index) => (
                  <div key={index} className="border-b border-gray-100 pb-4 last:border-b-0">
                    <h3 className="font-semibold text-gray-800 mb-2 line-clamp-2 text-lg">
                      {news.title}
                    </h3>
                    <p className="text-sm text-gray-600 mb-2 line-clamp-2">
                      {news.content}
                    </p>
                    <div className="flex justify-between items-center text-xs text-gray-500">
                      <span className="bg-red-100 text-red-700 px-2 py-1 rounded-full">{news.category}</span>
                      <span>{news.date}</span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-red-500 mx-auto mb-4"></div>
                  <p>핫뉴스를 불러오는 중입니다...</p>
                </div>
              )}
            </div>
          </div>

          {/* 실적뉴스 */}
          <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-lg">
            <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-3">
              <span className="text-2xl">📰</span>
              실적뉴스
            </h2>
            <div className="space-y-4">
              {mainNews.length > 0 ? (
                mainNews.slice(0, 5).map((news, index) => (
                  <div key={index} className="border-b border-gray-100 pb-4 last:border-b-0">
                    <h3 className="font-semibold text-gray-800 mb-2 line-clamp-2 text-lg">
                      {news.title}
                    </h3>
                    <p className="text-sm text-gray-600 mb-2 line-clamp-2">
                      {news.content}
                    </p>
                    <div className="flex justify-between items-center text-xs text-gray-500">
                      <span className="bg-green-100 text-green-700 px-2 py-1 rounded-full">{news.category}</span>
                      <span>{news.date}</span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-500 mx-auto mb-4"></div>
                  <p>실적뉴스를 불러오는 중입니다...</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* 중간: KOSPI 차트 */}
        <div className="bg-white rounded-2xl p-8 border border-gray-200 shadow-lg mb-8">
          <h2 className="text-3xl font-bold text-gray-800 mb-8 flex items-center gap-4">
            <span className="text-3xl">📈</span>
            KOSPI 최근 1년 시세 차트
          </h2>
          <div className="bg-gray-50 rounded-xl p-6">
            {chartData ? (
              <Line 
                data={chartData} 
                options={{
                  responsive: true,
                  plugins: {
                    legend: { display: false },
                    datalabels: { display: false },
                  },
                  scales: {
                    y: {
                      beginAtZero: false,
                      grid: {
                        color: 'rgba(0, 0, 0, 0.1)',
                      },
                      ticks: {
                        callback: (value: any) => value.toLocaleString() + ' pt',
                      },
                    },
                    x: {
                      grid: {
                        color: 'rgba(0, 0, 0, 0.1)',
                      },
                    },
                  },
                  elements: {
                    point: {
                      radius: 0,
                    },
                  },
                }}
              />
            ) : (
              <div className="text-center py-16 text-gray-500">
                <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mx-auto mb-6"></div>
                <p className="text-2xl">차트를 불러오는 중입니다...</p>
              </div>
            )}
          </div>
        </div>

        {/* 하단: 투자자별 매매 동향 */}
        <div className="bg-white rounded-2xl p-8 border border-gray-200 shadow-lg mb-8">
          <h2 className="text-3xl font-bold text-gray-800 mb-8 flex items-center gap-4">
            <span className="text-3xl">💰</span>
            KOSPI 투자자별 매매 동향
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-4 text-left text-lg font-semibold text-gray-700 border-b border-gray-200">투자자 구분</th>
                  <th className="px-6 py-4 text-center text-lg font-semibold text-gray-700 border-b border-gray-200">매도</th>
                  <th className="px-6 py-4 text-center text-lg font-semibold text-gray-700 border-b border-gray-200">매수</th>
                  <th className="px-6 py-4 text-center text-lg font-semibold text-gray-700 border-b border-gray-200">순매수</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {investorData.length > 0 ? (
                  investorData.map((item, index) => (
                    <tr key={index} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4 text-lg font-medium text-gray-900">{item.항목}</td>
                      <td className="px-6 py-4 text-lg text-center text-gray-700">{item.매도}</td>
                      <td className="px-6 py-4 text-lg text-center text-gray-700">{item.매수}</td>
                      <td className={`px-6 py-4 text-lg text-center font-semibold ${
                        (typeof item.순매수 === 'string' && item.순매수.startsWith('+')) || 
                        (typeof item.순매수 === 'number' && item.순매수 > 0) ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {typeof item.순매수 === 'number' ? 
                          (item.순매수 > 0 ? `+${item.순매수.toLocaleString()}` : item.순매수.toLocaleString()) : 
                          item.순매수
                        }
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={4} className="px-6 py-16 text-center text-gray-500">
                      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
                      <p className="text-lg">데이터를 불러오는 중입니다...</p>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* 왼쪽: TOP5 표들 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
          {/* 가입자 TOP 5 */}
          <div className="bg-white rounded-xl p-4 border border-gray-200 shadow-sm">
            <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
              <span className="text-xl">🏆</span>
              가입자 TOP 5
            </h3>
            <div className="space-y-2">
              <div className="flex justify-between items-center py-2 px-3 bg-gray-50 rounded-lg">
                <span className="font-medium text-gray-700 text-sm">AJ네트웍스</span>
                <span className="font-bold text-blue-600">0</span>
              </div>
              <div className="flex justify-between items-center py-2 px-3 bg-gray-50 rounded-lg">
                <span className="font-medium text-gray-700 text-sm">AK홀딩스</span>
                <span className="font-bold text-blue-600">0</span>
              </div>
              <div className="flex justify-between items-center py-2 px-3 bg-gray-50 rounded-lg">
                <span className="font-medium text-gray-700 text-sm">BGF</span>
                <span className="font-bold text-blue-600">0</span>
              </div>
              <div className="flex justify-between items-center py-2 px-3 bg-gray-50 rounded-lg">
                <span className="font-medium text-gray-700 text-sm">BGF리테일</span>
                <span className="font-bold text-blue-600">0</span>
              </div>
              <div className="flex justify-between items-center py-2 px-3 bg-gray-50 rounded-lg">
                <span className="font-medium text-gray-700 text-sm">BNK금융지주</span>
                <span className="font-bold text-blue-600">0</span>
              </div>
            </div>
          </div>

          {/* 시가총액 TOP 5 */}
          <div className="bg-white rounded-xl p-4 border border-gray-200 shadow-sm">
            <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
              <span className="text-xl">📊</span>
              시가총액 TOP 5
            </h3>
            <div className="space-y-2">
              <div className="flex justify-between items-center py-2 px-3 bg-gray-50 rounded-lg">
                <span className="font-medium text-gray-700 text-sm">AJ네트웍스</span>
                <span className="font-bold text-green-600">0.00</span>
              </div>
              <div className="flex justify-between items-center py-2 px-3 bg-gray-50 rounded-lg">
                <span className="font-medium text-gray-700 text-sm">AK홀딩스</span>
                <span className="font-bold text-green-600">0.00</span>
              </div>
              <div className="flex justify-between items-center py-2 px-3 bg-gray-50 rounded-lg">
                <span className="font-medium text-gray-700 text-sm">BGF</span>
                <span className="font-bold text-green-600">0.00</span>
              </div>
              <div className="flex justify-between items-center py-2 px-3 bg-gray-50 rounded-lg">
                <span className="font-medium text-gray-700 text-sm">BGF리테일</span>
                <span className="font-bold text-green-600">0.00</span>
              </div>
              <div className="flex justify-between items-center py-2 px-3 bg-gray-50 rounded-lg">
                <span className="font-medium text-gray-700 text-sm">BNK금융지주</span>
                <span className="font-bold text-green-600">0.00</span>
              </div>
            </div>
          </div>

          {/* 매출액 TOP 5 */}
          <div className="bg-white rounded-xl p-4 border border-gray-200 shadow-sm">
            <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
              <span className="text-xl">💰</span>
              매출액 TOP 5
            </h3>
            <div className="space-y-2">
              <div className="flex justify-between items-center py-2 px-3 bg-gray-50 rounded-lg">
                <span className="font-medium text-gray-700 text-sm">금성출판</span>
                <span className="font-bold text-purple-600">2,004,739</span>
              </div>
              <div className="flex justify-between items-center py-2 px-3 bg-gray-50 rounded-lg">
                <span className="font-medium text-gray-700 text-sm">현대차증권</span>
                <span className="font-bold text-purple-600">1,752,212</span>
              </div>
              <div className="flex justify-between items-center py-2 px-3 bg-gray-50 rounded-lg">
                <span className="font-medium text-gray-700 text-sm">현대해상</span>
                <span className="font-bold text-purple-600">1,286,908</span>
              </div>
              <div className="flex justify-between items-center py-2 px-3 bg-gray-50 rounded-lg">
                <span className="font-medium text-gray-700 text-sm">SK</span>
                <span className="font-bold text-purple-600">1,074,488</span>
              </div>
              <div className="flex justify-between items-center py-2 px-3 bg-gray-50 rounded-lg">
                <span className="font-medium text-gray-700 text-sm">기아</span>
                <span className="font-bold text-purple-600">932,889</span>
              </div>
            </div>
          </div>

          {/* 영업이익 TOP 5 */}
          <div className="bg-white rounded-xl p-4 border border-gray-200 shadow-sm">
            <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
              <span className="text-xl">📈</span>
              영업이익 TOP 5
            </h3>
            <div className="space-y-2">
              <div className="flex justify-between items-center py-2 px-3 bg-gray-50 rounded-lg">
                <span className="font-medium text-gray-700 text-sm">NAF엔터테인먼트</span>
                <span className="font-bold text-orange-600">80.21</span>
              </div>
              <div className="flex justify-between items-center py-2 px-3 bg-gray-50 rounded-lg">
                <span className="font-medium text-gray-700 text-sm">이카운트</span>
                <span className="font-bold text-orange-600">77.26</span>
              </div>
              <div className="flex justify-between items-center py-2 px-3 bg-gray-50 rounded-lg">
                <span className="font-medium text-gray-700 text-sm">시선테크</span>
                <span className="font-bold text-orange-600">68.10</span>
              </div>
              <div className="flex justify-between items-center py-2 px-3 bg-gray-50 rounded-lg">
                <span className="font-medium text-gray-700 text-sm">SK이노베이션</span>
                <span className="font-bold text-orange-600">67.57</span>
              </div>
              <div className="flex justify-between items-center py-2 px-3 bg-gray-50 rounded-lg">
                <span className="font-medium text-gray-700 text-sm">신한금융지주</span>
                <span className="font-bold text-orange-600">66.01</span>
              </div>
            </div>
          </div>

          {/* DPS TOP 5 */}
          <div className="bg-white rounded-xl p-4 border border-gray-200 shadow-sm">
            <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
              <span className="text-xl">🏆</span>
              DPS TOP 5
            </h3>
            <div className="space-y-2">
              <div className="flex justify-between items-center py-2 px-3 bg-gray-50 rounded-lg">
                <span className="font-medium text-gray-700 text-sm">한국철강</span>
                <span className="font-bold text-red-600">27,000</span>
              </div>
              <div className="flex justify-between items-center py-2 px-3 bg-gray-50 rounded-lg">
                <span className="font-medium text-gray-700 text-sm">한국생산성본부</span>
                <span className="font-bold text-red-600">19,000</span>
              </div>
              <div className="flex justify-between items-center py-2 px-3 bg-gray-50 rounded-lg">
                <span className="font-medium text-gray-700 text-sm">삼성화재해상보험</span>
                <span className="font-bold text-red-600">17,500</span>
              </div>
              <div className="flex justify-between items-center py-2 px-3 bg-gray-50 rounded-lg">
                <span className="font-medium text-gray-700 text-sm">고려아연</span>
                <span className="font-bold text-red-600">12,000</span>
              </div>
              <div className="flex justify-between items-center py-2 px-3 bg-gray-50 rounded-lg">
                <span className="font-medium text-gray-700 text-sm">현대자동차</span>
                <span className="font-bold text-red-600">10,000</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;

