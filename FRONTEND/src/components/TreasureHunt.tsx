'use client'

import React, { useEffect, useState } from 'react';
import { API_ENDPOINTS } from '../config/api';

interface TreasureData {
  기업명: string;
  업종명: string;
  PER: { [key: string]: number };
  PBR: { [key: string]: number };
  ROE: { [key: string]: number };
  지배주주지분: { [key: string]: number };
  지배주주순이익: { [key: string]: number };
  시가총액: { [key: string]: number };
}

function TreasureHunt() {
  const [data, setData] = useState<TreasureData[]>([]);
  const [filtered, setFiltered] = useState<TreasureData[]>([]);
  const [sortField, setSortField] = useState<string | null>(null);
  const [sortOrder, setSortOrder] = useState('asc');
  const [industryFilter, setIndustryFilter] = useState('전체');
  const [industries, setIndustries] = useState<string[]>([]);
  const [pbrMin, setPbrMin] = useState(0);
  const [pbrMax, setPbrMax] = useState(3);
  const [perMin, setPerMin] = useState(0);
  const [perMax, setPerMax] = useState(50);
  const [roeMin, setRoeMin] = useState(0);
  const [roeMax, setRoeMax] = useState(30);
  const [industryMetrics, setIndustryMetrics] = useState<any>(null);
  
  // 삼각형 다이어그램용 상태
  const [marketCap, setMarketCap] = useState<number>(0);
  const [equity, setEquity] = useState<number>(0);
  const [netIncome, setNetIncome] = useState<number>(0);

  useEffect(() => {
    fetch('/industry_metrics.json')
    .then(res => res.json())
    .then(setIndustryMetrics);

    fetch(API_ENDPOINTS.TREASURE_DATA)
      .then(res => res.json())
      .then(json => {
        const cleaned = json.filter((item: TreasureData) => {
          const hasAnyPER = Object.values(item.PER || {}).some(v => typeof v === 'number');
          const hasAnyPBR = Object.values(item.PBR || {}).some(v => typeof v === 'number');
          const hasAnyROE = Object.values(item.ROE || {}).some(v => typeof v === 'number');
          return hasAnyPER && hasAnyPBR && hasAnyROE;
        });
        setData(cleaned);
        setFiltered(cleaned);
        const uniqueIndustries = Array.from(new Set(cleaned.map((item: TreasureData) => item.업종명))).sort() as string[];
        setIndustries(['전체', ...uniqueIndustries]);
      })
      .catch(err => console.error('❌ 데이터 로딩 오류:', err));
  }, []);

  const applyFilters = () => {
    const filteredData = data.filter(item => {
      const perAvg = parseFloat(getThreeYearAvg(item.PER));
      const pbrAvg = parseFloat(getThreeYearAvg(item.PBR));
      const roeAvg = parseFloat(getThreeYearAvg(item.ROE));

      const isValid = ![perAvg, pbrAvg, roeAvg].some(val => isNaN(val) || val === 0);
      const matchIndustry = industryFilter === '전체' || item.업종명 === industryFilter;

      return (
        matchIndustry &&
        isValid &&
        perAvg >= perMin && perAvg <= perMax &&
        pbrAvg >= pbrMin && pbrAvg <= pbrMax &&
        roeAvg >= roeMin && roeAvg <= roeMax
      );
    });

    setFiltered(filteredData);
  };

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

  const handleSort = (field: string) => {
    const order = sortField === field && sortOrder === 'asc' ? 'desc' : 'asc';

    const sorted = [...filtered].sort((a, b) => {
      const aAvg = parseFloat(getThreeYearAvg(field === '시가총액' ? a.시가총액 : a[field as keyof TreasureData] as any)) || 0;
      const bAvg = parseFloat(getThreeYearAvg(field === '시가총액' ? b.시가총액 : b[field as keyof TreasureData] as any)) || 0;
      return order === 'asc' ? aAvg - bAvg : bAvg - aAvg;
    });

    setFiltered(sorted);
    setSortField(field);
    setSortOrder(order);
  };

  const labels = industryMetrics
    ? formatMetricHeaders(industryMetrics, industryFilter)
    : { PBR: 'PBR', PER: 'PER', ROE: 'ROE' };

  // 삼각형 다이어그램 계산 함수
  const calculatePBR = () => equity > 0 ? (marketCap / equity).toFixed(2) : '0.00';
  const calculatePER = () => netIncome > 0 ? (marketCap / netIncome).toFixed(2) : '0.00';
  const calculateROE = () => equity > 0 ? ((netIncome / equity) * 100).toFixed(2) : '0.00';

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 헤더 */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-full mb-6">
            <span className="text-3xl">💰</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-4">
            보물찾기
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            저평가 우량주를 찾아내는 스마트한 재무 분석 도구
          </p>
        </div>

        {/* 메인 컨테이너 */}
        <div className="bg-white rounded-3xl shadow-2xl border border-gray-100 overflow-hidden">
          {/* 필터 섹션 */}
          <div className="bg-gradient-to-r from-gray-50 to-blue-50 p-8 border-b border-gray-200">
            <div className="max-w-4xl mx-auto">
              <h2 className="text-2xl font-bold text-gray-800 mb-8 flex items-center gap-3">
                <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-sm">✔</span>
                </div>
                업종 선택 및 필터링
              </h2>
              
              <div className="flex flex-wrap items-center gap-4 mb-8">
            <select
              value={industryFilter}
              onChange={(e) => setIndustryFilter(e.target.value)}
                  className="px-6 py-4 border-2 border-gray-200 rounded-xl bg-white text-gray-700 focus:ring-4 focus:ring-blue-100 focus:border-blue-500 transition-all duration-200 min-w-[250px] text-lg font-medium"
                >
              {industries.map((industry, idx) => (
                <option key={idx} value={industry}>{industry}</option>
              ))}
            </select>

            <button
              onClick={applyFilters}
                  className="px-8 py-4 bg-gradient-to-r from-green-500 to-emerald-600 text-white font-bold rounded-xl hover:from-green-600 hover:to-emerald-700 transform hover:scale-105 transition-all duration-200 shadow-lg hover:shadow-xl"
                >
                  🔍 조건 적용
            </button>
              </div>

            {/* 슬라이더들 */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* PBR 범위 */}
                <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
                  <label className="block text-lg font-bold text-gray-800 mb-4">PBR 범위 (2024)</label>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-500 font-medium">최소</span>
                      <input 
                        type="number" 
                        value={pbrMin} 
                        onChange={(e) => setPbrMin(Number(e.target.value))} 
                        className="w-20 px-3 py-2 text-center border-2 border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-medium" 
                      />
                    </div>
                    <input 
                      type="range" 
                      min={0} max={15} step={0.1} value={pbrMin} 
                      onChange={(e) => setPbrMin(Number(e.target.value))} 
                      className="w-full h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer slider" 
                    />
                    <input 
                      type="range" 
                      min={0} max={15} step={0.1} value={pbrMax} 
                      onChange={(e) => setPbrMax(Number(e.target.value))} 
                      className="w-full h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer slider" 
                    />
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-500 font-medium">최대</span>
                      <input 
                        type="number" 
                        value={pbrMax} 
                        onChange={(e) => setPbrMax(Number(e.target.value))} 
                        className="w-20 px-3 py-2 text-center border-2 border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-medium" 
                      />
                    </div>
                  </div>
                </div>

                {/* PER 범위 */}
                <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
                  <label className="block text-lg font-bold text-gray-800 mb-4">PER 범위 (2024)</label>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-500 font-medium">최소</span>
                      <input 
                        type="number" 
                        value={perMin} 
                        onChange={(e) => setPerMin(Number(e.target.value))} 
                        className="w-20 px-3 py-2 text-center border-2 border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-medium" 
                      />
                    </div>
                    <input 
                      type="range" 
                      min={0} max={100} step={0.1} value={perMin} 
                      onChange={(e) => setPerMin(Number(e.target.value))} 
                      className="w-full h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer slider" 
                    />
                    <input 
                      type="range" 
                      min={0} max={100} step={0.1} value={perMax} 
                      onChange={(e) => setPerMax(Number(e.target.value))} 
                      className="w-full h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer slider" 
                    />
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-500 font-medium">최대</span>
                      <input 
                        type="number" 
                        value={perMax} 
                        onChange={(e) => setPerMax(Number(e.target.value))} 
                        className="w-20 px-3 py-2 text-center border-2 border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-medium" 
                      />
                    </div>
                  </div>
                </div>

                {/* ROE 범위 */}
                <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
                  <label className="block text-lg font-bold text-gray-800 mb-4">ROE 범위 (2024)</label>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-500 font-medium">최소</span>
                      <input 
                        type="number" 
                        value={roeMin} 
                        onChange={(e) => setRoeMin(Number(e.target.value))} 
                        className="w-20 px-3 py-2 text-center border-2 border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-medium" 
                      />
                    </div>
                    <input 
                      type="range" 
                      min={-50} max={80} step={0.1} value={roeMin} 
                      onChange={(e) => setRoeMin(Number(e.target.value))} 
                      className="w-full h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer slider" 
                    />
                    <input 
                      type="range" 
                      min={-50} max={80} step={0.1} value={roeMax} 
                      onChange={(e) => setRoeMax(Number(e.target.value))} 
                      className="w-full h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer slider" 
                    />
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-500 font-medium">최대</span>
                      <input 
                        type="number" 
                        value={roeMax} 
                        onChange={(e) => setRoeMax(Number(e.target.value))} 
                        className="w-20 px-3 py-2 text-center border-2 border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-medium" 
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* 주요 재무 지표 섹션 */}
          <div className="p-8">
            <div className="max-w-4xl mx-auto text-center mb-12">
              <h2 className="text-3xl md:text-4xl font-bold text-gray-800 mb-4">
                주요 재무 지표 한 눈에 알아보기!
              </h2>
              <p className="text-xl text-gray-600 mb-8">
                당신이 대주주를 꿈꾼다면 알아야 할 핵심 지표
              </p>

              {/* 삼각형 다이어그램 */}
              <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-3xl p-8 border-2 border-blue-100 shadow-lg">
                <div className="relative w-96 h-80 mx-auto">
                  {/* 상단 꼭지점 - 시가총액 */}
                  <div className="absolute top-0 left-1/2 transform -translate-x-1/2 text-center z-10">
                    <div className="text-sm font-bold text-gray-700 mb-2">시가총액</div>
                    <input 
                      type="number" 
                      placeholder="시가총액 입력" 
                      value={marketCap || ''} 
                      onChange={(e) => setMarketCap(Number(e.target.value))}
                      className="w-32 px-4 py-3 text-center border-2 border-blue-300 rounded-xl focus:ring-4 focus:ring-blue-100 focus:border-blue-500 font-bold text-blue-600 text-lg" 
                    />
                  </div>

                  {/* 좌하단 꼭지점 - 지배주주지분 */}
                  <div className="absolute bottom-0 left-0 text-center z-10">
                    <div className="text-sm font-bold text-gray-700 mb-2">지배주주지분</div>
                    <input 
                      type="number" 
                      placeholder="지배주주지분 입력" 
                      value={equity || ''} 
                      onChange={(e) => setEquity(Number(e.target.value))}
                      className="w-28 px-3 py-2 text-center border-2 border-green-300 rounded-xl focus:ring-4 focus:ring-green-100 focus:border-green-500 font-bold text-green-600" 
                    />
            </div>

                  {/* 우하단 꼭지점 - 지배주주순이익 */}
                  <div className="absolute bottom-0 right-0 text-center z-10">
                    <div className="text-sm font-bold text-gray-700 mb-2">지배주주순이익</div>
                    <input 
                      type="number" 
                      placeholder="지배주주순이익 입력" 
                      value={netIncome || ''} 
                      onChange={(e) => setNetIncome(Number(e.target.value))}
                      className="w-28 px-3 py-2 text-center border-2 border-red-300 rounded-xl focus:ring-4 focus:ring-red-100 focus:border-red-500 font-bold text-red-600" 
                    />
            </div>

                  {/* 삼각형 선들 */}
                  <svg width="384" height="320" className="absolute top-0 left-0 z-1 pointer-events-none">
                    {/* 좌측 선 - PBR */}
                    <line x1="192" y1="40" x2="0" y2="280" stroke="#3b82f6" strokeWidth="6" />
                    <text x="96" y="160" textAnchor="middle" fill="#3b82f6" fontSize="18" fontWeight="bold">PBR: {calculatePBR()}</text>
                    
                    {/* 우측 선 - PER */}
                    <line x1="192" y1="40" x2="384" y2="280" stroke="#10b981" strokeWidth="6" />
                    <text x="288" y="160" textAnchor="middle" fill="#10b981" fontSize="18" fontWeight="bold">PER: {calculatePER()}</text>
                    
                    {/* 하단 선 - ROE */}
                    <line x1="0" y1="280" x2="384" y2="280" stroke="#ef4444" strokeWidth="6" />
                    <text x="192" y="310" textAnchor="middle" fill="#ef4444" fontSize="18" fontWeight="bold">ROE: {calculateROE()}%</text>
                  </svg>

                  {/* 중앙 아이콘 */}
                  <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-4xl">
                    🏢
                  </div>
            </div>
          </div>

              {/* 공식 설명 */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-12">
                <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm">
                  <h3 className="text-lg font-bold text-gray-800 mb-4">기본 공식</h3>
                  <div className="space-y-3 text-sm text-gray-700">
                    <div><strong>PBR = 시가총액 / 지배주주지분</strong></div>
                    <div><strong>PER = 시가총액 / 지배주주순이익</strong></div>
                    <div><strong>ROE = 지배주주순이익 / 지배주주지분 × 100</strong></div>
                  </div>
                </div>
                <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm">
                  <h3 className="text-lg font-bold text-gray-800 mb-4">상세 설명</h3>
                  <div className="space-y-3 text-sm text-gray-700">
                    <div><strong>지배주주순이익 = 당기순이익 - 비지배주주순이익(세후)</strong></div>
                    <div><strong>지배주주지분 = 자본총계 - 비지배주주지분(자본)</strong></div>
                  </div>
                </div>
          </div>
        </div>

            {/* 정렬 버튼들 */}
            <div className="flex flex-wrap gap-3 mb-8 justify-center">
              <button 
                onClick={() => handleSort('시가총액')}
                className="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-bold rounded-xl hover:from-purple-600 hover:to-pink-600 transform hover:scale-105 transition-all duration-200 shadow-lg"
              >
                📊 시가총액 정렬
              </button>
              <button 
                onClick={() => handleSort('PBR')}
                className="px-6 py-3 bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-bold rounded-xl hover:from-blue-600 hover:to-cyan-600 transform hover:scale-105 transition-all duration-200 shadow-lg"
              >
                📈 PBR 정렬
              </button>
              <button 
                onClick={() => handleSort('PER')}
                className="px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-500 text-white font-bold rounded-xl hover:from-green-600 hover:to-emerald-600 transform hover:scale-105 transition-all duration-200 shadow-lg"
              >
                📉 PER 정렬
              </button>
              <button 
                onClick={() => handleSort('ROE')}
                className="px-6 py-3 bg-gradient-to-r from-orange-500 to-red-500 text-white font-bold rounded-xl hover:from-orange-600 hover:to-red-600 transform hover:scale-105 transition-all duration-200 shadow-lg"
              >
                💰 ROE 정렬
              </button>
        </div>

            {/* 데이터 테이블 */}
            <div className="bg-white rounded-2xl border border-gray-200 shadow-lg overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gradient-to-r from-gray-50 to-blue-50">
                    <tr>
                      <th className="px-6 py-4 text-left text-sm font-bold text-gray-700 border-b border-gray-200">기업명</th>
                      <th className="px-6 py-4 text-left text-sm font-bold text-gray-700 border-b border-gray-200">업종명</th>
                      <th className="px-6 py-4 text-center text-sm font-bold text-gray-700 border-b border-gray-200" colSpan={4}>{labels.PBR}</th>
                      <th className="px-6 py-4 text-center text-sm font-bold text-gray-700 border-b border-gray-200" colSpan={4}>{labels.PER}</th>
                      <th className="px-6 py-4 text-center text-sm font-bold text-gray-700 border-b border-gray-200" colSpan={4}>{labels.ROE}</th>
                      <th className="px-6 py-4 text-center text-sm font-bold text-gray-700 border-b border-gray-200">지배주주지분<br/>(2024)</th>
                      <th className="px-6 py-4 text-center text-sm font-bold text-gray-700 border-b border-gray-200">지배주주순이익<br/>(2024)</th>
                      <th className="px-6 py-4 text-center text-sm font-bold text-gray-700 border-b border-gray-200">시가총액<br/>(2024)</th>
            </tr>
            <tr>
                      <th className="px-6 py-3 text-center text-xs text-gray-500 border-b border-gray-100">2022</th>
                      <th className="px-6 py-3 text-center text-xs text-gray-500 border-b border-gray-100">2023</th>
                      <th className="px-6 py-3 text-center text-xs text-gray-500 border-b border-gray-100">2024</th>
                      <th className="px-6 py-3 text-center text-xs text-gray-500 border-b border-gray-100">3년평균</th>
                      <th className="px-6 py-3 text-center text-xs text-gray-500 border-b border-gray-100">2022</th>
                      <th className="px-6 py-3 text-center text-xs text-gray-500 border-b border-gray-100">2023</th>
                      <th className="px-6 py-3 text-center text-xs text-gray-500 border-b border-gray-100">2024</th>
                      <th className="px-6 py-3 text-center text-xs text-gray-500 border-b border-gray-100">3년평균</th>
                      <th className="px-6 py-3 text-center text-xs text-gray-500 border-b border-gray-100">2022</th>
                      <th className="px-6 py-3 text-center text-xs text-gray-500 border-b border-gray-100">2023</th>
                      <th className="px-6 py-3 text-center text-xs text-gray-500 border-b border-gray-100">2024</th>
                      <th className="px-6 py-3 text-center text-xs text-gray-500 border-b border-gray-100">3년평균</th>
            </tr>
          </thead>
                  <tbody className="divide-y divide-gray-100">
            {filtered.map((item, idx) => (
                      <tr key={idx} className="hover:bg-gray-50 transition-colors">
                        <td className="px-6 py-4 text-sm font-medium text-gray-900">{item.기업명}</td>
                        <td className="px-6 py-4 text-sm text-gray-600">{item.업종명}</td>
                        <td className="px-6 py-4 text-sm text-center text-gray-600">{item.PBR?.['2022'] ?? '-'}</td>
                        <td className="px-6 py-4 text-sm text-center text-gray-600">{item.PBR?.['2023'] ?? '-'}</td>
                        <td className="px-6 py-4 text-sm text-center text-gray-600">{item.PBR?.['2024'] ?? '-'}</td>
                        <td className="px-6 py-4 text-sm text-center font-bold bg-blue-50">{getThreeYearAvg(item.PBR)}</td>
                        <td className="px-6 py-4 text-sm text-center text-gray-600">{item.PER?.['2022'] ?? '-'}</td>
                        <td className="px-6 py-4 text-sm text-center text-gray-600">{item.PER?.['2023'] ?? '-'}</td>
                        <td className="px-6 py-4 text-sm text-center text-gray-600">{item.PER?.['2024'] ?? '-'}</td>
                        <td className="px-6 py-4 text-sm text-center font-bold bg-green-50">{getThreeYearAvg(item.PER)}</td>
                        <td className="px-6 py-4 text-sm text-center text-gray-600">{item.ROE?.['2022'] ?? '-'}</td>
                        <td className="px-6 py-4 text-sm text-center text-gray-600">{item.ROE?.['2023'] ?? '-'}</td>
                        <td className="px-6 py-4 text-sm text-center text-gray-600">{item.ROE?.['2024'] ?? '-'}</td>
                        <td className="px-6 py-4 text-sm text-center font-bold bg-red-50">{getThreeYearAvg(item.ROE)}</td>
                        <td className="px-6 py-4 text-sm text-center text-gray-600">{item.지배주주지분?.['2024']?.toLocaleString() ?? '-'}</td>
                        <td className="px-6 py-4 text-sm text-center text-gray-600">{item.지배주주순이익?.['2024']?.toLocaleString() ?? '-'}</td>
                        <td className="px-6 py-4 text-sm text-center text-gray-600">
                  {item.시가총액?.['2024']
                    ? (item.시가총액['2024'] / 100000000).toFixed(1) : '-'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default TreasureHunt;
