'use client'

import React, { useEffect, useState } from 'react';
import { useParams, useSearchParams } from 'next/navigation';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend
} from 'chart.js';
import ChartDataLabels from 'chartjs-plugin-datalabels';


ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend, ChartDataLabels);

const metricList = ["PER", "PBR", "ROE", "DPS"];

interface CompanyMetrics {
  PER: { [key: string]: number };
  PBR: { [key: string]: number };
  ROE: { [key: string]: number };
}

interface IndustryData {
  companies: string[];
  [key: string]: any;
}

interface AnalysisData {
  industry: string;
  analysis: {
    개요?: string;
    요약?: string | { [key: string]: string };
    "주요 재무 지표 해석"?: {
      [key: string]: {
        "산업 평균": string | number;
        "해석": string;
      };
    };
    "산업 체크포인트"?: Array<{
      항목: string;
      설명: string;
    }>;
  };
}

// 누락된 요약 섹션을 동적으로 생성하는 함수
function generateIndustrySummary(industry: string, analysis: any): string {
  // 이미 요약이 있으면 그대로 반환
  if (analysis.요약) {
    return typeof analysis.요약 === 'string' ? analysis.요약 : JSON.stringify(analysis.요약);
  }

  // 산업별 기본 요약 템플릿
  const summaryTemplates: { [key: string]: string } = {
    "IT 서비스": "IT 서비스 기업은 겉보기에 자산도 적고, 공장도 없고, 재고도 없으니까 '가벼운 사업'처럼 보이지만, 좋은 회사는 어마어마한 수익 창출력을 가지고 있어. 그걸 판단하는 건 숫자보다 비즈니스 모델의 질과 확장성을 보는 눈이야.",
    "건설": "건설업은 회사가 건물을 짓는 게 아니라, '현금 흐름 관리'를 짓는 산업이야. 공사 마진은 얇고, 리스크는 큽니다. 그래서 보수적인 재무구조와 철저한 수주관리가 중요하지.",
    "기계": "기계 장비 회사가 매력적이 되려면 아래 조건을 갖춰야 해.\n✅ 단순 조립 아닌 독자 기술력\n✅ 반복 매출(수주 + 서비스 매출)\n✅ 해외 진출 or 틈새시장 점유율\n✅ 영업현금흐름이 꾸준히 플러스\n✅ 고객사 다변화",
    "기타금융": "기타금융은 자산을 빌려주고 이자 받는 사업이야. 그러니까심은 다음 세 가지야:\n1. 돈을 얼마나 싸게 조달하느냐?\n2. 빌려준 돈을 얼마나 잘 회수하느냐?\n3. 경기 나쁠 때 얼마나 손실을 감당할 수 있느냐?",
    "기타제조": "✅ 투자 관점에서 좋은 기타제조 기업은?\n• 독점 납품처 혹은 장기 공급 계약이 있음\n• OEM 구조라도 고부가·고정밀 가공 기술 보유\n• 낮은 부채, 안정적 현금흐름, 고정비 구조 효율적\n• 외형 성장보다 이익의 질이 탄탄\n• ESG나 리쇼어링 수혜주로서 포지션이 있는 기업",
    "농업, 임업 및 어업": "✅ 투자 매력 기업 특징\n• 스마트팜, 자동화 양식, 고부가 종자/기술 보유 → 기술로 진입장벽 구축\n• 수출 경쟁력 보유 (김, 과일, 한우, 목재 등) → 글로벌 시세 노출\n• 정책 수혜 가능한 친환경·탄소흡수형 사업모델 보유\n'농·임·어업은 작고 느리지만 세상을 먹여 살리는 산업이다.'",
    "보험": "보험산업은 보험영업 + 자산운용의 이중 수익 구조를 갖고 있어. 핵심은 다음 세 가지야:\n1. 지속 가능한 보험 포트폴리오\n2. 변동성 낮은 자산운용 실력\n3. 위험 대비 충분한 자본여력",
    "금융": "✅ 좋은 금융기업의 특징\n• 수익성 + 안정성 균형 (ROE 10% 이상, 부채비율 안정적)\n• 차별화된 비즈니스 모델 (카드, 보험, 자산운용 등)\n• 디지털 전환 + 고객 경험 개선\n• 리스크 관리 체계 + 규제 대응 능력\n• 해외 진출 + 신사업 확장",
    "금속": "✅ 좋은 금속기업의 특징\n• 시황에 상관없이 꾸준한 현금흐름 확보 가능 (특수강, 고부가 소재 등)\n• 고객사 다변화 + 고정 공급계약 체결된 구조\n• 비용 절감, 자동화 설비 투자 잘한 기업 (고정비 절감)\n• ESG 대응 투자 선제적으로 한 곳 (예: 전기로 방식 철강)\n• 해외 수출 경쟁력 확보 기업",
    "섬유의복": "✅ 투자 매력 기업 특징\n• 브랜드 파워 + 디자인 역량 보유\n• 온라인 채널 + 글로벌 진출 성공\n• 지속가능 소재 + ESG 대응\n• 고부가 제품 + 프리미엄 포지셔닝\n• 효율적 공급망 + 비용 통제",
    "운수업": "✅ 좋은 운수업 기업의 특징\n• 안정적 수익구조 + 장기 계약 기반\n• 디지털 전환 + 효율성 향상\n• ESG 대응 + 친환경 기술 도입\n• 해외 진출 + 신사업 확장\n• 현금흐름 안정성 + 배당 지속성",
    "음식료품": "✅ 투자 매력 기업 특징\n• 브랜드 파워 + 고객 충성도\n• 건강식품 + 프리미엄 제품 라인업\n• 해외 진출 + 글로벌 시장 점유율\n• 효율적 공급망 + 비용 통제\n• 신제품 개발 + R&D 투자",
    "의료정밀": "✅ 좋은 의료정밀 기업의 특징\n• 독자 기술력 + 특허 포트폴리오\n• 글로벌 인증 + 해외 진출\n• 고부가 제품 + 프리미엄 포지셔닝\n• R&D 투자 + 신제품 개발\n• 규제 대응 + 품질 관리",
    "전기·전자": "✅ 투자 매력 기업 특징\n• 핵심 기술력 + 특허 보유\n• 글로벌 시장 점유율 + 브랜드 파워\n• 신기술 선도 + R&D 투자\n• 수직계열화 + 원가 경쟁력\n• ESG 대응 + 친환경 기술",
    "전기·가스": "✅ 좋은 전기·가스 기업의 특징\n• 안정적 수익구조 + 규제 환경\n• 친환경 에너지 + 신재생에너지\n• 효율성 향상 + 디지털 전환\n• 지역 독점 + 장기 계약\n• 현금흐름 안정성 + 배당 지속성",
    "제조업": "✅ 투자 관점에서 좋은 제조업 기업은?\n• 독점 납품처 혹은 장기 공급 계약이 있음\n• OEM 구조라도 고부가·고정밀 가공 기술 보유\n• 낮은 부채, 안정적 현금흐름, 고정비 구조 효율적\n• 외형 성장보다 이익의 질이 탄탄\n• ESG나 리쇼어링 수혜주로서 포지션이 있는 기업",
    "화학": "✅ 좋은 화학기업의 특징\n• 수직계열화 + 고부가 제품 비중↑\n• 제품/고객 다변화 → 스프레드 방어력\n• 환율 상승 수혜 + 안정적 원재료 조달\n• 특수소재(2차전지, 반도체 등) 매출 증가\n• 특허 기반 R&D 투자 → 진입장벽 형성",
    "부동산": "✅ 좋은 부동산 기업의 특징\n• 우량 자산 보유 (강남 오피스, 역세권 상가 등)\n• 임대료 인상 여력 + 공실률 낮은 구조\n• 부채비율 안정적 + 이자보상배율 3배 이상\n• 사업 다각화 (리츠, PM, 개발 등)\n• 배당 지속성 + 리파이낸싱 능력 보유",
    "일반서비스": "✅ 좋은 일반 서비스 기업의 특징\n• 고객 락인 구조 + 반복 매출 중심\n• 고정비 통제 + 자동화/디지털 전환에 투자 중\n• 현금흐름 꾸준 + 배당 여력 보유\n• 진입장벽 높은 규제 산업 (폐기물, 경비 등)\n• B2B 계약 비중 높은 기업 → 외부 변수에 강함"
  };

  // 기본 요약이 있으면 반환
  if (summaryTemplates[industry]) {
    return summaryTemplates[industry];
  }

  // 기본 요약이 없으면 분석 데이터를 기반으로 동적 생성
  let summary = `📊 ${industry} 산업 분석 요약\n\n`;
  
  if (analysis.개요) {
    summary += `🔍 산업 개요:\n${analysis.개요}\n\n`;
  }
  
  if (analysis["주요 재무 지표 해석"]) {
    summary += `📈 주요 재무 지표:\n`;
    Object.entries(analysis["주요 재무 지표 해석"]).forEach(([metric, data]: [string, any]) => {
      if (data["산업 평균"]) {
        summary += `• ${metric}: ${data["산업 평균"]}\n`;
      }
    });
    summary += '\n';
  }
  
  if (analysis["산업 체크포인트"]) {
    summary += `✅ 핵심 체크포인트:\n`;
    analysis["산업 체크포인트"].forEach((checkpoint: any) => {
      summary += `• ${checkpoint.항목}: ${checkpoint.설명}\n`;
    });
  }

  return summary;
}

function IndustryAnalysis() {
  const params = useParams();
  const searchParams = useSearchParams();
  const industry = decodeURIComponent(params?.industryName as string || '');
  const initialCompany = searchParams.get("company");

  const [analysis, setAnalysis] = useState<AnalysisData | null>(null);
  const [allData, setAllData] = useState<{ [key: string]: IndustryData } | null>(null);
  const [companyMetrics, setCompanyMetrics] = useState<{ [key: string]: any } | null>(null);
  const [selectedMetric, setSelectedMetric] = useState("PER");
  const [error, setError] = useState(false);

  const [companyList, setCompanyList] = useState<string[]>([]);
  const [selectedCompanyLeft, setSelectedCompanyLeft] = useState(initialCompany || "");
  const [selectedCompanyRight, setSelectedCompanyRight] = useState("");
  const [leftMetrics, setLeftMetrics] = useState<CompanyMetrics | null>(null);
  const [rightMetrics, setRightMetrics] = useState<CompanyMetrics | null>(null);
  const [industryMetrics, setIndustryMetrics] = useState<IndustryData | null>(null);

  console.log("🔍 params:", params);
  console.log("🔍 industry:", industry);
  console.log("🔍 initialCompany:", initialCompany);

  useEffect(() => {
    fetch("/industry_metrics.json")
      .then(res => res.json())
      .then(data => {
        const companies = data[industry!]?.companies || [];
        const sorted = [...companies].sort();
        setCompanyList(sorted);
        if (!initialCompany && sorted.length > 0) {
          setSelectedCompanyLeft(sorted[0]);
        }
      })
      .catch(err => {
        console.error("📛 industry_metrics.json 로드 실패:", err);
        setError(true);
      });
  }, [industry]);

  useEffect(() => {
    if (initialCompany) {
      setSelectedCompanyLeft(initialCompany);
      setSelectedCompanyRight("");
    } else {
      setSelectedCompanyLeft("");
      setSelectedCompanyRight("");
    }
  }, [initialCompany]);

  useEffect(() => {
    fetch("/산업별설명.json")
      .then(res => res.json())
      .then(data => {
        const industryAnalysis = data.find((item: AnalysisData) => item.industry === industry);
        setAnalysis(industryAnalysis || null);
      })
      .catch(err => {
        console.error("📛 산업별설명.json 로드 실패:", err);
        // 오류가 발생해도 계속 진행
      });
  }, [industry]);

  useEffect(() => {
    fetch("/industry_metrics.json")
      .then(res => res.json())
      .then(data => {
        setAllData(data);
        setIndustryMetrics(data[industry!] || null);
      })
      .catch(err => {
        console.error("📛 industry_metrics.json 로드 실패:", err);
        setError(true);
      });
  }, [industry]);

  // 기업별 재무지표 데이터 로드
  useEffect(() => {
    fetch("/기업별_재무지표.json")
      .then(res => res.json())
      .then(data => {
        setCompanyMetrics(data);
        console.log("✅ 기업별 재무지표 로드 성공:", Object.keys(data).length, "개 기업");
      })
      .catch(err => {
        console.error("📛 기업별_재무지표.json 로드 실패:", err);
      });
  }, []);

  const getThreeYearAvg = (obj: { [key: string]: number }): string => {
    const years = ['2022', '2023', '2024'];
    const values = years.map(year => obj?.[year]).filter(v => typeof v === 'number');
    if (!values.length) return '-';
    const avg = values.reduce((a, b) => a + b, 0) / values.length;
    return avg.toFixed(2);
  };

  const getAverage = (obj: any): string => {
    const nums = Object.values(obj ?? {}).map(Number).filter(v => !isNaN(v));
    const sum = nums.reduce((a, b) => a + b, 0);
    return nums.length ? (sum / nums.length).toFixed(2) : '-';
  };

  const formatMetricHeaders = (metrics: any, 업종명: string) => {
    if (!metrics || !metrics[업종명]) return {
      PBR: 'PBR',
      PER: 'PER',
      ROE: 'ROE',
    };
    const avg = metrics[업종명];
    return {
      PBR: `PBR (KOSPI 산업평균: ${getAverage(avg.PBR)})`,
      PER: `PER (KOSPI 산업평균: ${getAverage(avg.PER)})`,
      ROE: `ROE (KOSPI 산업평균: ${getAverage(avg.ROE)})`,
    };
  };

  const labels = allData ? formatMetricHeaders(allData, industry) : { PBR: 'PBR', PER: 'PER', ROE: 'ROE' };

  if (error) {
      return (
      <div className="min-h-screen bg-gradient-to-br from-red-50 to-pink-100 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">😵</div>
          <h1 className="text-2xl font-bold text-gray-800 mb-2">데이터 로드 실패</h1>
          <p className="text-gray-600">산업 데이터를 불러오는데 실패했습니다.</p>
        </div>
        </div>
      );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* 헤더 */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-full mb-6">
            <span className="text-3xl">🏭</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-4">
            {industry} 산업 분석
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            산업 요약 및 주요 재무 지표 분석
          </p>
        </div>

        {/* 메인 컨테이너 */}
        <div className="bg-white rounded-3xl shadow-2xl border border-gray-100 overflow-hidden">
          <div className="p-8">
            {/* 산업 요약 - 모든 산업에 표시 */}
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl p-6 border border-blue-100 mb-8">
              <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center gap-3">
                <span className="text-2xl">💡</span>
                산업 요약
              </h2>
              <div className="text-gray-700 leading-relaxed text-lg">
                {analysis?.analysis?.요약 ? (
                  typeof analysis.analysis.요약 === 'string' ? (
                    <p>{analysis.analysis.요약}</p>
                  ) : (
                    <div>
                      {Object.entries(analysis.analysis.요약).map(([key, value], idx) => (
                        <div key={idx} className="mb-4">
                          <h4 className="font-bold text-gray-800 mb-2">{key}</h4>
                          <p>{Array.isArray(value) ? value.join(', ') : value}</p>
                        </div>
                      ))}
                    </div>
                  )
                ) : analysis?.analysis?.개요 ? (
                  <p>{analysis.analysis.개요}</p>
                ) : (
                  <p>📊 {industry} 산업에 대한 요약 정보를 불러오는 중입니다...</p>
                )}
              </div>
            </div>

            {/* 주요 재무 지표 해석 */}
            {analysis?.analysis?.["주요 재무 지표 해석"] && (
              <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl p-6 border border-green-100 mb-8">
                <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-3">
                  <span className="text-2xl">📊</span>
                  주요 재무 지표 해석
                </h2>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {Object.entries(analysis.analysis["주요 재무 지표 해석"]).map(([key, value]) => (
                    <div key={key} className="bg-white rounded-xl p-6 border border-green-200">
                      <h3 className="text-lg font-bold text-gray-800 mb-3">{key}</h3>
                      <div className="space-y-3">
                        <div>
                          <span className="font-semibold text-green-700">산업 평균:</span>
                          <span className="ml-2 text-gray-700">{value["산업 평균"]}</span>
                        </div>
                        <div>
                          <span className="font-semibold text-green-700">해석:</span>
                          <p className="mt-1 text-gray-700 text-sm leading-relaxed">{value["해석"]}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 산업 체크포인트 */}
            {analysis?.analysis?.["산업 체크포인트"] && (
              <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-2xl p-6 border border-purple-100 mb-8">
                <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-3">
                  <span className="text-2xl">✅</span>
                  산업 체크포인트
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {analysis.analysis["산업 체크포인트"].map((item, index) => (
                    <div key={index} className="bg-white rounded-xl p-6 border border-purple-200">
                      <h3 className="text-lg font-bold text-gray-800 mb-3">{item.항목}</h3>
                      <p className="text-gray-700 text-sm leading-relaxed">{item.설명}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 코스피 기준 재무 지표 */}
            <div className="bg-gradient-to-br from-yellow-50 to-orange-50 rounded-2xl p-6 border border-yellow-100 mb-8">
              <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-3">
                <span className="text-2xl">📈</span>
                코스피 기준 {industry} 업종 주요 재무 지표
              </h2>
              <div className="flex flex-wrap gap-3 mb-6">
                {metricList.map((metric) => (
            <button
              key={metric}
              onClick={() => setSelectedMetric(metric)}
                    className={`px-6 py-3 rounded-xl font-bold transition-all duration-200 ${
                      selectedMetric === metric
                        ? 'bg-gradient-to-r from-yellow-500 to-orange-500 text-white shadow-lg'
                        : 'bg-white border-2 border-yellow-200 text-gray-700 hover:border-yellow-300'
                    }`}
            >
              {metric}
            </button>
          ))}
        </div>

              {/* 차트 영역 */}
              <div className="bg-white rounded-xl p-6 border border-yellow-200">
                {industryMetrics ? (
                  <Line
                    data={{
                      labels: ['2022', '2023', '2024'],
                      datasets: [{
                        label: '코스피 기준 업종 평균',
                        data: [
                          industryMetrics[selectedMetric]?.['2022'] || 0,
                          industryMetrics[selectedMetric]?.['2023'] || 0,
                          industryMetrics[selectedMetric]?.['2024'] || 0
                        ],
                        borderColor: '#8b5cf6',
                        backgroundColor: 'rgba(139, 92, 246, 0.1)',
                        tension: 0.3,
                        pointRadius: 3,
                        borderWidth: 2,
                      }]
                    }}
                    options={{
                      responsive: true,
                      plugins: {
                        legend: { display: true },
                        tooltip: {
                          callbacks: {
                            label: (context: any) => `${context.dataset.label}: ${context.parsed.y.toFixed(2)}`
                          }
                        }
                      },
                      scales: {
                        y: {
                          beginAtZero: false,
                          ticks: {
                            callback: function(value) {
                              return Number(value).toFixed(2);
                            }
                          }
                        }
                      }
                    }}
                  />
                ) : (
                  <div className="text-center py-12 text-gray-500">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-500 mx-auto mb-4"></div>
                    차트 데이터를 불러오는 중입니다...
                  </div>
                )}
              </div>
      </div>

            {/* 동종 산업 내 기업 비교하기 */}
            <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-2xl p-6 border border-blue-100 mb-8">
              <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-3">
                <span className="text-2xl">🔍</span>
                동종 산업 내 기업 비교하기
              </h2>
              
              {/* 기업 선택 드롭다운 */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">기준 기업</label>
                  <select
                    value={selectedCompanyLeft}
                    onChange={(e) => setSelectedCompanyLeft(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">기업 선택</option>
                    {companyList.map((company) => (
                      <option key={company} value={company}>{company}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">비교 기업</label>
                  <select
                    value={selectedCompanyRight}
                    onChange={(e) => setSelectedCompanyRight(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">기업 선택</option>
                    {companyList.map((company) => (
                      <option key={company} value={company}>{company}</option>
                    ))}
                  </select>
                </div>
              </div>

              {/* 비교 차트들 */}
              {selectedCompanyLeft && selectedCompanyRight && (
                <div className="space-y-8">
                  {['PER', 'PBR', 'ROE'].map((metric) => (
                    <div key={metric} className="bg-white rounded-xl p-6 border border-blue-200">
                      <h3 className="text-lg font-bold text-gray-800 mb-4 text-center">{metric} 추이</h3>
                      <Line
                        data={{
                          labels: ['2022', '2023', '2024'],
                          datasets: [
                            {
                              label: selectedCompanyLeft,
                              data: [
                                allData?.[industry]?.[selectedCompanyLeft]?.[metric]?.['2022'] || 0,
                                allData?.[industry]?.[selectedCompanyLeft]?.[metric]?.['2023'] || 0,
                                allData?.[industry]?.[selectedCompanyLeft]?.[metric]?.['2024'] || 0
                              ],
                              borderColor: '#3b82f6',
                              backgroundColor: 'rgba(59, 130, 246, 0.1)',
                              tension: 0.3,
                              pointRadius: 3,
                              borderWidth: 2,
                            },
                            {
                              label: selectedCompanyRight,
                              data: [
                                allData?.[industry]?.[selectedCompanyRight]?.[metric]?.['2022'] || 0,
                                allData?.[industry]?.[selectedCompanyRight]?.[metric]?.['2023'] || 0,
                                allData?.[industry]?.[selectedCompanyRight]?.[metric]?.['2024'] || 0
                              ],
                              borderColor: '#10b981',
                              backgroundColor: 'rgba(16, 185, 129, 0.1)',
                              tension: 0.3,
                              pointRadius: 3,
                              borderWidth: 2,
                            },
                            {
                              label: '코스피 기준 업종 평균',
                              data: [
                                industryMetrics?.[metric]?.['2022'] || 0,
                                industryMetrics?.[metric]?.['2023'] || 0,
                                industryMetrics?.[metric]?.['2024'] || 0
                              ],
                              borderColor: '#f59e0b',
                              backgroundColor: 'rgba(245, 158, 11, 0.1)',
                              tension: 0.3,
                              pointRadius: 3,
                              borderWidth: 2,
                            }
                          ]
                        }}
                        options={{
                          responsive: true,
                          plugins: {
                            legend: { display: true },
                            tooltip: {
                              callbacks: {
                                label: (context: any) => `${context.dataset.label}: ${context.parsed.y.toFixed(2)}`
                              }
                            }
                          },
                          scales: {
                            y: {
                              beginAtZero: false,
                              ticks: {
                                callback: function(value) {
                                  return Number(value).toFixed(2);
                                }
                              }
                            }
                          }
                        }}
                      />
                    </div>
                  ))}
                </div>
              )}
            </div>


        </div>
        </div>
      </div>
    </div>
  );
}

export default IndustryAnalysis;
