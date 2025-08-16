'use client'

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { useRouter } from 'next/navigation';
import { Line, Bar, Pie } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Title,
  Tooltip,
  Legend,
  BarElement,
  ArcElement,
} from 'chart.js';
import SalesTable from './SalesTable';
import CompanySummary from './CompanySummary';
import CompareChart from './CompareChart';
import PieChart from './PieChart';
import ShareholderChart from './ShareholderChart';
import api, { API_ENDPOINTS } from '../config/api';

ChartJS.register(
  LineElement, 
  PointElement, 
  LinearScale, 
  CategoryScale, 
  Title, 
  Tooltip, 
  Legend,
  BarElement,
  ArcElement
);

interface CompanyDetailProps {
  companyName?: string;
}

interface Company {
  기업명: string;
  업종명: string;
  종목코드: string;
  짧은요약: any;
  개요: any;
  지표: any;
}

interface PriceData {
  Date: string;
  Close: number;
}

interface NewsItem {
  title: string;
  link: string;
  content?: string;
  date?: string;
  category?: string;
}

interface ReportItem {
  date: string;
  title: string;
  analyst: string;
  summary: string;
  target_price: string;
}

interface InvestorItem {
  date: string;
  기관합계: number;
  개인: number;
  외국인합계: number;
}

function CompanyDetail({ companyName }: CompanyDetailProps) {
  const params = useParams();
  const name = companyName || params?.name as string;
  const router = useRouter();
  const [company, setCompany] = useState<Company | null>(null);
  const [priceData, setPriceData] = useState<PriceData[]>([]);
  const [news, setNews] = useState<NewsItem[]>([]);
  const [report, setReport] = useState<ReportItem[]>([]);
  const [investors, setInvestors] = useState<InvestorItem[]>([]);
  const [error, setError] = useState(false);
  const [showSalesTable, setShowSalesTable] = useState(false);
  const [metrics, setMetrics] = useState<any>(null);
  const [industryMetrics, setIndustryMetrics] = useState<any>(null);
  const [jsonIndicators, setJsonIndicators] = useState<any>(null);
  const [openDescriptions, setOpenDescriptions] = useState<{[key: string]: boolean}>({});
  // const [companyOverview, setCompanyOverview] = useState<any>(null);
  
  const toggleDescription = (metric: string) => {
    setOpenDescriptions(prev => ({...prev, [metric]: !prev[metric]}));
  };



  const metricDescriptions: {[key: string]: string} = {
    'PER': '주가가 그 회사의 이익에 비해 비싼지 싼지를 보는 숫자야. 숫자가 낮으면 "이 회사 주식이 싸네?"라고 생각할 수 있어.',
    'PBR': '회사가 가진 재산에 비해 주식이 얼마나 비싼지를 알려줘. 숫자가 높으면 "자산은 별론데 주가는 높네"일 수도 있어.',
    'ROE': '내가 투자한 돈으로 회사가 얼마나 똑똑하게 돈을 벌었는지 보여줘. 높을수록 "잘 굴리고 있네!"라는 뜻이야.',
    'ROA': '회사가 가진 모든 자산(돈, 건물 등)을 얼마나 잘 써서 이익을 냈는지 보여줘. 효율이 좋은 회사일수록 높아.',
    'DPS': '주식 1주를 가진 사람이 1년 동안 받는 배당금이야. 이 숫자가 높으면 "이 주식은 배당이 쏠쏠하네"라고 볼 수 있어.',
    'EPS': '회사가 1년에 벌어들인 이익을 주식 1주당 얼마씩 나눠 가질 수 있는지 보여줘. 많이 벌면 좋겠지!',
    'BPS': '회사가 망하고 나서 자산을 팔았을 때 주식 1주당 받을 수 있는 돈이야. 일종의 바닥 가격 같은 거야.',
    '부채비율': '회사 자본에 비해 빚이 얼마나 많은지 보여줘. 숫자가 너무 높으면 위험하다는 뜻이야.',
    '배당수익률': '이 주식을 샀을 때 1년 동안 배당으로 얼마를 벌 수 있는지 비율로 알려줘. 높으면 현금 수익이 괜찮은 거야.',
    '영업이익률': '매출에서 실제 이익이 얼마나 남았는지를 비율로 보여줘. 높을수록 본업에서 돈 잘 버는 회사야.',
    '당기순이익': '회사가 1년 동안 진짜로 벌어들인 순이익이야. 세금 등 다 빼고 남은 돈이야.',
    '매출액': '회사가 물건이나 서비스를 팔아서 벌어들인 총 매출이야. 아직 비용은 안 뺀 금액이야.',
    '영업이익': '본업으로 벌어들인 이익이야. 매출에서 인건비, 임대료 같은 비용을 뺀 금액이야.',
  };

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
        console.log("🏢 기업 정보 API 호출 중...");
        const companyRes = await api.get(API_ENDPOINTS.COMPANY(name));
        console.log("✅ 기업 정보 성공:", companyRes.data);
        setCompany(companyRes.data);

        // 기업 정보를 받은 후 종목코드로 다른 API 호출
        const code = String(companyRes.data.종목코드).padStart(6, '0');
        const ticker = code + '.KS';

        // 병렬로 API 호출하여 성능 향상
        const [priceRes, newsRes, reportRes, investorsRes] = await Promise.allSettled([
          api.get(API_ENDPOINTS.STOCK_PRICE(ticker)),
          api.get(API_ENDPOINTS.COMPANY_NEWS(name)),
          api.get(API_ENDPOINTS.ANALYST_REPORT(`A${code}`)),
          api.get(API_ENDPOINTS.INVESTOR_SUMMARY(code))
        ]);

        if (priceRes.status === 'fulfilled') {
          console.log("✅ 주가 데이터 성공:", priceRes.value.data);
          setPriceData(priceRes.value.data);
        }
        if (newsRes.status === 'fulfilled') {
          console.log("✅ 뉴스 성공:", newsRes.value.data);
          setNews(newsRes.value.data);
        }
        if (reportRes.status === 'fulfilled') {
          console.log("✅ 애널리스트 리포트 성공:", reportRes.value.data);
          setReport(reportRes.value.data);
        }
        if (investorsRes.status === 'fulfilled') {
          console.log("✅ 투자자 동향 성공:", investorsRes.value.data);
          setInvestors(investorsRes.value.data);
        }

      } catch (err) {
        console.error("❌ 기업 정보 오류:", err);
        setError(true);
      }
    };

    if (name) {
      fetchData();
    }
  }, [name]);

  useEffect(() => {
    fetch("/기업별_재무지표.json")
      .then(res => res.json())
      .then(data => {
        if (data[name]) {
          setMetrics(data[name]);
        }
      })
      .catch(err => console.error("재무지표 로드 실패:", err));
  }, [name]);

  useEffect(() => {
    fetch("/industry_metrics.json")
      .then(res => res.json())
      .then(data => {
        if (company && data[company.업종명]) {
          setIndustryMetrics(data[company.업종명]);
        }
      })
      .catch(err => console.error("산업 지표 로드 실패:", err));
  }, [company]);

  useEffect(() => {
    fetch('/기업별_재무지표.json')
      .then(res => res.json())
      .then(data => setJsonIndicators(data))
      .catch(err => console.error('❌ JSON 불러오기 실패:', err));
  }, []);

  // 기업 개요 데이터는 백엔드 API를 통해 가져와야 함
  // useEffect(() => {
  //   // 백엔드 API 호출로 대체 필요
  // }, [name]);

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-50 to-pink-100 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">😵</div>
          <h1 className="text-2xl font-bold text-gray-800 mb-2">기업 정보 로드 실패</h1>
          <p className="text-gray-600">기업 정보를 불러오는데 실패했습니다.</p>
        </div>
      </div>
    );
  }

  if (!company) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">기업 정보를 불러오는 중입니다...</p>
        </div>
      </div>
    );
  }

  const code = company.종목코드;
  
  // 기존 JSX 로직: company.지표에서 데이터 파싱
  const rawIndicators = company.지표 || {};
  const indicatorMap: any = {};
  const allPeriods = new Set();

  for (const [key, value] of Object.entries(rawIndicators)) {
    if (!value || value === 0) continue;
    const parts = (key as string).split('_');
    if (parts.length < 2) continue;

    const period = parts[0];
    const metric = parts.slice(1).join('_');

    if (!indicatorMap[metric]) indicatorMap[metric] = {};
    indicatorMap[metric][period] = value;
    allPeriods.add(period);
  }

  const sortedPeriods = Array.from(allPeriods)
    .filter((period) => period !== '2025/05')  // 제외
    .sort() as string[];
  const sortedMetrics = Object.keys(indicatorMap).sort();

  function calcAverage(values: any[]): number | null {
    const validValues = values.filter(v => v !== null && v !== undefined && !isNaN(v));
    if (validValues.length === 0) return null;
    const average = validValues.reduce((a, b) => a + b, 0) / validValues.length;
    return Number(average.toFixed(2));
  }

  function extractMetricValues(map: any, metric: string): any[] {
    return ["2022", "2023", "2024"].map(year => map[metric]?.[year]);
  }

  function generateComparisonText(metricName: string, companyName: string, companyVals: any[], industryVals: any[]) {
    const companyAvg = calcAverage(companyVals);
    const industryAvg = calcAverage(industryVals);

    if (companyAvg === null || industryAvg === null) {
      return (
        <span>
          <strong className="text-blue-600 text-lg">{companyName}</strong>
          의 <strong className="text-gray-800">{metricName}</strong> 데이터가 부족하여{' '}
          <span className="text-red-600 font-bold">비교할 수 없습니다.</span>
        </span>
      );
    }

    const diff = Math.abs(companyAvg - industryAvg);
    const comparison = companyAvg > industryAvg ? '상향' : '하향';

    let threshold = 5;
    if (metricName === 'PBR') threshold = 0.5;
    if (metricName === 'ROE') threshold = 7;

    const gap = diff < threshold ? '근소한 차이를 보이고 있어.' : '큰 격차를 보이고 있어.';

    return (
      <span className="text-xl">
        <strong className="text-blue-600">{companyName}</strong>
        는 3개년 <strong className="text-gray-800">{metricName}</strong> 평균이
        <strong className="text-orange-600"> {companyAvg}</strong>로,
        코스피 기준 업종 평균
        <strong className="text-green-600"> {industryAvg}</strong>보다
        <span className={`font-bold ${comparison === '상향' ? 'text-red-600' : 'text-blue-600'}`}>
          {' '}{comparison}
        </span>
        하며 {gap}
      </span>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 p-6">
      <div className="max-w-full mx-auto">
        {/* 헤더 */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-full mb-6">
            <span className="text-3xl">🏢</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-4">
            {company.기업명}
          </h1>
          <div className="flex justify-center items-center gap-8 text-lg text-gray-600">
            <span>업종: {company.업종명}</span>
            <span>종목코드: {code}</span>
          </div>
        </div>

        {/* 메인 컨테이너 */}
        <div className="bg-white rounded-3xl shadow-2xl border border-gray-100 overflow-hidden">
          <div className="p-8">
            {/* 기업 요약 */}
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl p-6 border border-blue-100 mb-8">
              <CompanySummary summary={company.짧은요약} outline={company.개요} />
            </div>

            {/* 기업 개요 */}
            {company.개요 && (
              <div className="bg-gradient-to-br from-gray-50 to-slate-50 rounded-2xl p-8 border-2 border-gray-200 shadow-xl mb-8">
                <h2 className="text-3xl font-bold text-gray-800 mb-8 flex items-center gap-4">
                  <span className="text-3xl">🏢</span>
                  기업 개요
                </h2>
                <div className="bg-white rounded-2xl border-2 border-gray-200 overflow-hidden shadow-lg">
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-gradient-to-r from-gray-100 to-slate-100">
                        <tr>
                          <th className="px-8 py-6 text-left text-xl font-bold text-gray-800 border-b-2 border-gray-200">구분</th>
                          <th className="px-8 py-6 text-left text-xl font-bold text-gray-800 border-b-2 border-gray-200">내용</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y-2 divide-gray-100">
                        {Object.entries(company.개요).map(([key, value]) => (
                          <tr key={key} className="hover:bg-gray-50 transition-all duration-300 group">
                            <td className="px-8 py-6 text-xl font-bold text-gray-900">{key}</td>
                            <td className="px-8 py-6 text-xl text-gray-700">
                              {key.toLowerCase().includes('홈페이지') || key.toLowerCase().includes('url') ? (
                                <a href={value as string} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:text-blue-800 font-semibold transition-colors duration-200 hover:underline">
                                  {value as string}
                                </a>
                              ) : (
                                value as string
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}

            {/* 주가 차트 */}
            <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl p-6 border border-green-100 mb-8">
              <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-3">
                <span className="text-2xl">📈</span>
                {company.기업명} 최근 3년 주가
              </h2>
              <div className="bg-white rounded-xl p-6 border border-green-200">
                {priceData.length > 0 ? (
                  <Line
                    data={{
                      labels: priceData.map(item => item.Date),
                      datasets: [{
                        label: `${company.기업명} 종가 (원)`,
                        data: priceData.map(item => item.Close),
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        tension: 0.3,
                        pointRadius: 0,
                        pointHoverRadius: 0,
                        borderWidth: 3,
                      }]
                    }}
                    options={{
                      responsive: true,
                      plugins: {
                        legend: { display: true },
                        tooltip: {
                          callbacks: {
                            title: (context: any) => `날짜: ${context[0].label}`,
                            label: (context: any) => `${context.parsed.y.toLocaleString()} 원`
                          }
                        },
                        datalabels: {
                          display: false
                        }
                      },
                      scales: {
                        x: {
                          ticks: {
                            display: false
                          },
                          grid: {
                            display: false
                          }
                        },
                        y: {
                          ticks: {
                            callback: (value: any) => value.toLocaleString() + ' 원'
                          }
                        }
                      },
                      elements: {
                        point: {
                          radius: 0,
                          hoverRadius: 0
                        }
                      }
                    }}
                  />
                ) : (
                  <div className="text-center py-12 text-gray-500">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500 mx-auto mb-4"></div>
                    주가 데이터를 불러오는 중입니다...
                  </div>
                )}
              </div>
            </div>

            {/* 기업 뉴스 */}
            <div className="bg-gradient-to-br from-red-50 to-pink-50 rounded-2xl p-6 border border-red-100 mb-8">
              <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-3">
                <span className="text-2xl">📰</span>
                {company.기업명} 관련 뉴스
              </h2>
              <div className="space-y-4">
                {news.length > 0 ? (
                  news.slice(0, 5).map((item, index) => (
                    <div key={index} className="bg-white rounded-xl p-4 border border-red-200 hover:shadow-md transition-shadow">
                      <h3 className="font-semibold text-gray-800 mb-2 line-clamp-2">
                        <a href={item.link} target="_blank" rel="noopener noreferrer" className="hover:text-red-600 transition-colors">
                          {item.title}
                        </a>
                      </h3>
                      {item.content && (
                        <p className="text-sm text-gray-600 mb-2 line-clamp-2">{item.content}</p>
                      )}
                      <div className="flex justify-between items-center text-xs text-gray-500">
                        {item.category && <span className="bg-red-100 text-red-700 px-2 py-1 rounded-full">{item.category}</span>}
                        {item.date && <span>{item.date}</span>}
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-red-500 mx-auto mb-4"></div>
                    뉴스를 불러오는 중입니다...
                  </div>
                )}
              </div>
            </div>

            {/* 애널리스트 리포트 */}
            <div className="bg-gradient-to-br from-purple-50 to-indigo-50 rounded-2xl p-6 border border-purple-100 mb-8">
              <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-3">
                <span className="text-2xl">📊</span>
                애널리스트 리포트
              </h2>
              <div className="space-y-4">
                {report.length > 0 ? (
                  report.slice(0, 3).map((item, index) => (
                    <div key={index} className="bg-white rounded-xl p-4 border border-purple-200 hover:shadow-md transition-shadow">
                      <h3 className="font-semibold text-gray-800 mb-2">{item.title}</h3>
                      <p className="text-sm text-gray-600 mb-2 line-clamp-2">{item.summary}</p>
                      <div className="flex justify-between items-center text-xs text-gray-500">
                        <span>애널리스트: {item.analyst}</span>
                        <span>목표가: {item.target_price}</span>
                        <span>{item.date}</span>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500 mx-auto mb-4"></div>
                    리포트를 불러오는 중입니다...
                  </div>
                )}
              </div>
            </div>

            {/* 기업 투자자별 매매동향 */}
            <div className="bg-gradient-to-br from-yellow-50 to-orange-50 rounded-2xl p-6 border border-yellow-100 mb-8">
              <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-3">
                <span className="text-2xl">💰</span>
                {company.기업명} 투자자별 매매동향
              </h2>
              <div className="bg-white rounded-xl border border-yellow-200 overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gradient-to-r from-yellow-100 to-orange-100">
                      <tr>
                        <th className="px-6 py-4 text-left text-lg font-semibold text-gray-700 border-b border-yellow-200">날짜</th>
                        <th className="px-6 py-4 text-center text-lg font-semibold text-gray-700 border-b border-yellow-200">기관합계</th>
                        <th className="px-6 py-4 text-center text-lg font-semibold text-gray-700 border-b border-yellow-200">개인</th>
                        <th className="px-6 py-4 text-center text-lg font-semibold text-gray-700 border-b border-yellow-200">외국인합계</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-yellow-100">
                      {investors.length > 0 ? (
                        investors.slice(0, 10).map((item, index) => (
                          <tr key={index} className="hover:bg-yellow-50 transition-colors">
                            <td className="px-6 py-4 text-lg font-medium text-gray-900">{item.date}</td>
                            <td className={`px-6 py-4 text-lg text-center font-semibold ${item.기관합계 > 0 ? 'text-green-600' : 'text-red-600'}`}>
                              {item.기관합계 > 0 ? `+${item.기관합계.toLocaleString()}` : item.기관합계.toLocaleString()}
                            </td>
                            <td className={`px-6 py-4 text-lg text-center font-semibold ${item.개인 > 0 ? 'text-green-600' : 'text-red-600'}`}>
                              {item.개인 > 0 ? `+${item.개인.toLocaleString()}` : item.개인.toLocaleString()}
                            </td>
                            <td className={`px-6 py-4 text-lg text-center font-semibold ${item.외국인합계 > 0 ? 'text-green-600' : 'text-red-600'}`}>
                              {item.외국인합계 > 0 ? `+${item.외국인합계.toLocaleString()}` : item.외국인합계.toLocaleString()}
                            </td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan={4} className="px-6 py-16 text-center text-gray-500">
                            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-500 mx-auto mb-4"></div>
                            <p className="text-lg">투자자 동향을 불러오는 중입니다...</p>
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            {/* 지분 구조 */}
            <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-2xl p-6 border border-purple-100 mb-8">
              <ShareholderChart code={code} companyName={company.기업명} />
            </div>

            {/* 제품별 매출 비중과 세부표 */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
              {/* 제품별 매출 비중 */}
              <div className="bg-gradient-to-br from-yellow-50 to-orange-50 rounded-2xl p-6 border border-yellow-100">
                <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-3">
                  <span className="text-2xl">📊</span>
                  제품별 매출 비중
                </h2>
                <PieChart companyName={company.기업명} />
              </div>

              {/* 매출 구성 세부표 */}
              <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-2xl p-6 border border-indigo-100">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-3">
                    <span className="text-2xl">📁</span>
                    매출 구성 세부표
                  </h2>
                  <button
                    onClick={() => setShowSalesTable(prev => !prev)}
                    className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                  >
                    {showSalesTable ? '숨기기 ▲' : '보기 ▼'}
                  </button>
                </div>
                {showSalesTable && (
                  <div className="bg-white rounded-xl p-4 border border-indigo-200">
                    <SalesTable name={company.기업명} />
                  </div>
                )}
              </div>
            </div>

            {/* 재무 지표 섹션 */}
            <div className="bg-gradient-to-br from-red-50 to-pink-50 rounded-2xl p-6 border border-red-100 mb-8">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-3xl font-bold text-gray-800 flex items-center gap-3">
                  <span className="text-3xl">📊</span>
                  기업 주요 재무 지표
                </h2>
                <button
                  onClick={() => router.push(`/industry/${encodeURIComponent(company.업종명)}?company=${encodeURIComponent(company.기업명)}`)}
                  className="px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white font-bold rounded-xl hover:from-green-600 hover:to-emerald-700 transform hover:scale-105 transition-all duration-200 shadow-lg"
                >
                  📊 다른 기업과 비교하기
                </button>
              </div>

              <div className="bg-white rounded-xl p-6 border border-red-200 mb-6">
                <p className="text-gray-700 text-lg leading-relaxed mb-4">
                  기업의 재무 지표를 <strong>표</strong>와 <strong>그래프</strong> 형태로 표현했어!<br />
                  표에서는 <strong>연도별 수치</strong>를 확인할 수 있고, 그래프에서는 <strong>{company.업종명} 업종 평균과 비교한 추이</strong>를 시각적으로 확인할 수 있어!
                </p>
                <p className="text-gray-700 text-lg">
                  <u><strong>🪄 버튼을 누르면 설명이 나와!</strong></u>
                </p>
              </div>

              {/* 원본 재무지표 테이블 */}
              <div className="bg-white rounded-2xl border-2 border-red-200 overflow-hidden shadow-xl">
                <div className="p-8 border-b-2 border-red-200 bg-gradient-to-r from-red-50 to-pink-50">
                  <div className="flex justify-between items-center">
                    <h3 className="text-2xl font-bold text-gray-800 flex items-center gap-3">
                      <span className="text-2xl">📑</span>
                      재무지표 (원본 데이터)
                    </h3>
                    <span className="text-lg text-gray-600 font-medium">매출액,당기순이익,영업이익(단위: 억 원)</span>
                  </div>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gradient-to-r from-red-100 to-pink-100">
                      <tr>
                        <th className="px-8 py-6 text-left text-lg font-bold text-gray-800 border-b-2 border-red-200">지표명</th>
                        {sortedPeriods.map(period => (
                          <th key={period} className="px-8 py-6 text-center text-lg font-bold text-gray-800 border-b-2 border-red-200">
                            {period}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y-2 divide-red-100">
                      {sortedMetrics.filter(metric => !metric.includes('.1') && metric !== '시가총액').map((metric) => (
                        <tr key={metric} className="hover:bg-red-50 transition-all duration-300 group">
                          <td className="px-8 py-6 text-lg font-semibold text-gray-900">
                            <div className="flex items-center gap-3">
                              <span className="text-xl">{metric}</span>
                              <button
                                onClick={() => toggleDescription(metric)}
                                className="text-blue-600 hover:text-blue-800 text-lg transition-colors duration-200 hover:scale-110"
                              >
                                {openDescriptions[metric] ? '▼' : '▶'}
                              </button>
                            </div>
                            {openDescriptions[metric] && (
                              <div className="mt-4 p-4 bg-blue-50 rounded-xl text-sm text-gray-700 border border-blue-200 shadow-md">
                                {metricDescriptions[metric]}
                              </div>
                            )}
                          </td>
                          {sortedPeriods.map(period => {
                            const value = indicatorMap[metric][period];
                            return (
                              <td key={period} className="px-8 py-6 text-lg text-center text-gray-700 font-medium">
                                {value !== undefined ? Number(value).toLocaleString() : '-'}
                              </td>
                            );
                          })}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* 업종 비교 차트 */}
              {industryMetrics && jsonIndicators && jsonIndicators[name] && (
                <div className="mt-8 bg-white rounded-2xl border-2 border-red-200 overflow-hidden shadow-xl">
                  <div className="p-8 border-b-2 border-red-200 bg-gradient-to-r from-blue-50 to-indigo-50">
                    <h3 className="text-2xl font-bold text-gray-800 flex items-center gap-3">
                      <span className="text-2xl">📈</span>
                      업종 평균과 비교한 재무지표 그래프
                    </h3>
                  </div>
                  <div className="p-8">
                    <div className="grid grid-cols-1 gap-8">
                      {['PER', 'PBR', 'ROE'].map(metric => (
                        <div key={metric} className="bg-gray-50 rounded-xl p-6">
                          <CompareChart
                            metrics={jsonIndicators[name]}
                            industryMetrics={industryMetrics}
                            companyName={company.기업명}
                            metricType={metric}
                          />
                          <div className="mt-4 text-center text-sm text-gray-700">
                            {(() => {
                              const companyVals = extractMetricValues(jsonIndicators[name], metric);
                              const industryVals = extractMetricValues(industryMetrics, metric);
                              return generateComparisonText(metric, company.기업명, companyVals, industryVals);
                            })()}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>


          </div>
        </div>
      </div>
    </div>
  );
}

export default CompanyDetail;
