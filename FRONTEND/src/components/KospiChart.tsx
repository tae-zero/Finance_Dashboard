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

interface KospiData {
  Date: string;
  Close: number;
}

export default function KospiChart() {
  const [kospiData, setKospiData] = useState<KospiData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchKospiData = async () => {
      try {
        setLoading(true);
        const response = await api.get(API_ENDPOINTS.KOSPI_DATA);
        
        const data = response.data;
        setKospiData(data);
        setError(null);
      } catch (err) {
        console.error('코스피 데이터 오류:', err);
        setError('데이터를 불러올 수 없습니다.');
        // 기본 데이터로 fallback
        setKospiData([
          { Date: '2024-01', Close: 2500 },
          { Date: '2024-02', Close: 2550 },
          { Date: '2024-03', Close: 2600 },
          { Date: '2024-04', Close: 2650 },
          { Date: '2024-05', Close: 2700 },
          { Date: '2024-06', Close: 2750 },
          { Date: '2024-07', Close: 2800 },
          { Date: '2024-08', Close: 2850 },
          { Date: '2024-09', Close: 2900 },
          { Date: '2024-10', Close: 2950 },
          { Date: '2024-11', Close: 3000 },
          { Date: '2024-12', Close: 3220 }
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchKospiData();
  }, []);

  if (loading) {
    return (
      <div className="h-80 bg-gray-100 rounded-lg flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">코스피 데이터 로딩 중...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="h-80 bg-red-50 rounded-lg flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-2">{error}</p>
          <p className="text-sm text-gray-500">기본 데이터를 표시합니다.</p>
        </div>
      </div>
    );
  }

  // 차트 데이터 구성
  const chartData = {
    labels: kospiData.map(item => {
      const date = new Date(item.Date);
      return `${date.getMonth() + 1}월`;
    }),
    datasets: [
      {
        label: 'KOSPI 지수',
        data: kospiData.map(item => item.Close),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
        fill: true,
        pointBackgroundColor: 'rgb(59, 130, 246)',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 5,
        pointHoverRadius: 8,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          font: {
            size: 12,
            weight: 'bold' as const
          }
        }
      },
      title: {
        display: true,
        text: 'KOSPI 최근 1년 시세 추이',
        font: {
          size: 16,
          weight: 'bold' as const
        }
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
        callbacks: {
          label: function(context: any) {
            return `KOSPI: ${context.parsed.y.toLocaleString()}`;
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: false,
        // 편차를 더 크게 만들어 시각화 개선
        min: Math.min(...kospiData.map(item => item.Close)) * 0.85,
        max: Math.max(...kospiData.map(item => item.Close)) * 1.15,
        ticks: {
          callback: function(value: any) {
            return value.toLocaleString();
          },
          font: {
            size: 11
          }
        },
        grid: {
          color: 'rgba(0, 0, 0, 0.1)'
        }
      },
      x: {
        grid: {
          color: 'rgba(0, 0, 0, 0.1)'
        },
        ticks: {
          font: {
            size: 11
          }
        }
      }
    },
    interaction: {
      mode: 'nearest' as const,
      axis: 'x' as const,
      intersect: false
    }
  };

  return (
    <div className="h-80">
      <Line data={chartData} options={options} />
    </div>
  );
}
