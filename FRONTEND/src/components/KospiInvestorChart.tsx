'use client'

import React, { useState, useEffect } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';
import api, { API_ENDPOINTS } from '../config/api';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface InvestorData {
  date: string;
  individual: number;
  foreign: number;
  institution: number;
  financial: number;
  insurance: number;
  investment: number;
  bank: number;
  pension: number;
  other: number;
}

export default function KospiInvestorChart() {
  const [investorData, setInvestorData] = useState<InvestorData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchInvestorData = async () => {
      try {
        setLoading(true);
        const response = await api.get(API_ENDPOINTS.INVESTOR_VALUE);
        
        // 백엔드에서 {data: {...}} 형태로 반환하므로 response.data.data로 접근
        const data = response.data.data || response.data;
        
        if (!data || !data.투자자별_거래량 || !Array.isArray(data.투자자별_거래량)) {
          console.warn('투자자 데이터 구조 오류:', response.data);
          throw new Error('투자자 데이터 구조가 올바르지 않습니다.');
        }
        
        setInvestorData(data.투자자별_거래량);
        setError(null);
      } catch (err) {
        console.error('투자자 데이터 오류:', err);
        setError('데이터를 불러올 수 없습니다.');
      } finally {
        setLoading(false);
      }
    };

    fetchInvestorData();
  }, []);

  if (loading) {
    return (
      <div className="h-80 bg-gray-100 rounded-lg flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">데이터를 불러오는 중입니다...</p>
        </div>
      </div>
    );
  }

  if (error || investorData.length === 0) {
    return (
      <div className="h-80 bg-red-50 rounded-lg flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-2">{error || '투자자 데이터가 없습니다.'}</p>
        </div>
      </div>
    );
  }

  // 최신 데이터 사용 (가장 최근 날짜)
  const latestData = investorData[investorData.length - 1];
  
  // 차트 데이터 구성
  const chartData = {
    labels: ['개인', '외국인', '기관', '금융투자', '보험', '투신', '은행', '연기금', '기타법인'],
    datasets: [
      {
        label: '거래량 (백만원)',
        data: [
          latestData.individual / 1000000,
          latestData.foreign / 1000000,
          latestData.institution / 1000000,
          latestData.financial / 1000000,
          latestData.insurance / 1000000,
          latestData.investment / 1000000,
          latestData.bank / 1000000,
          latestData.pension / 1000000,
          latestData.other / 1000000,
        ],
        backgroundColor: [
          'rgba(255, 99, 132, 0.8)',
          'rgba(54, 162, 235, 0.8)',
          'rgba(255, 206, 86, 0.8)',
          'rgba(75, 192, 192, 0.8)',
          'rgba(153, 102, 255, 0.8)',
          'rgba(255, 159, 64, 0.8)',
          'rgba(199, 199, 199, 0.8)',
          'rgba(83, 102, 255, 0.8)',
          'rgba(78, 252, 3, 0.8)',
        ],
        borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(153, 102, 255, 1)',
          'rgba(255, 159, 64, 1)',
          'rgba(199, 199, 199, 1)',
          'rgba(83, 102, 255, 1)',
          'rgba(78, 252, 3, 1)',
        ],
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: `KOSPI 투자자별 거래량 (${latestData.date})`,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: '거래량 (백만원)',
        },
      },
    },
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg">
      <h3 className="text-xl font-bold mb-4 text-center">💰 KOSPI 투자자별 매매 동향</h3>
      <div className="h-80">
        <Bar data={chartData} options={options} />
      </div>
      <div className="mt-4 text-sm text-gray-600 text-center">
        <p>최근 거래일: {latestData.date}</p>
        <p>개인: {Math.round(latestData.individual / 1000000)}백만원 | 
           외국인: {Math.round(latestData.foreign / 1000000)}백만원 | 
           기관: {Math.round(latestData.institution / 1000000)}백만원</p>
      </div>
    </div>
  );
}
