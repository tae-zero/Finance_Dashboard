'use client'

import React, { useEffect, useState } from 'react';
import { Pie } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from 'chart.js';
import ChartDataLabels from 'chartjs-plugin-datalabels';

ChartJS.register(ArcElement, Tooltip, Legend, ChartDataLabels);

interface CompanyData {
  종목명: string;
  data: Array<{
    label: string;
    value: number;
  }>;
}

interface PieChartProps {
  companyName: string;
}

function PieChart({ companyName }: PieChartProps) {
  const [companyData, setCompanyData] = useState<CompanyData | null>(null);

  useEffect(() => {
    if (!companyName) return;

    console.log('🔍 PieChart: 기업명 검색 중:', companyName);
    
    fetch('/매출비중_chartjs_데이터.json')
      .then(res => res.json())
      .then(json => {
        console.log('📊 PieChart: 전체 데이터 로드됨, 개수:', json.length);
        const matched = json.find((item: CompanyData) => item.종목명 === companyName);
        console.log('🎯 PieChart: 매칭된 데이터:', matched);
        if (matched) {
          setCompanyData(matched);
        } else {
          console.warn('⚠️ PieChart: 매칭되는 기업 데이터가 없습니다');
        }
      })
      .catch(err => {
        console.error("📛 PieChart 데이터 로딩 오류:", err);
      });
  }, [companyName]);

  if (!companyData) return <p>📉 매출 데이터를 불러오는 중입니다...</p>;

  const data = companyData.data;
  const chartData = {
    labels: data.map(item => item.label),
    datasets: [
      {
        label: '제품별 매출비중',
        data: data.map(item => item.value),
        backgroundColor: [
          '#4e79a7', '#f28e2c', '#e15759', '#76b7b2', '#59a14f',
          '#edc949', '#af7aa1', '#ff9da7', '#9c755f', '#bab0ab'
        ],
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    layout: {
      padding: {
        top: 10, // 👉 그래프 내부 여백만 살짝
        bottom: 10,
        left: 20,
        right: 20,
      },
    },
    plugins: {
        legend: {
            position: 'bottom' as const,
            align: 'start' as const, // ✅ 실제로 왼쪽 정렬 시도
            labels: {
              boxWidth: 18,
              padding: 10,
              font: { size: 12 },
              textAlign: 'left' as const, // ❌ 잘 안 먹히지만 추가
            },
            fullSize: true,
          },

      datalabels: {
        color: '#000',
        font: {
          weight: 'bold' as const,
          size: 12,
        },
        offset: 10,
        clamp: true,
        align: (ctx: any) => {
          const value = ctx.dataset.data[ctx.dataIndex];
          const total = ctx.chart._metasets[0].total;
          const percent = (value / total) * 100;
          return percent >= 10 ? 'center' : 'end';
        },
        anchor: (ctx: any) => {
          const value = ctx.dataset.data[ctx.dataIndex];
          const total = ctx.chart._metasets[0].total;
          const percent = (value / total) * 100;
          return percent >= 10 ? 'center' : 'end';
        },
        formatter: (value: number, context: any) => {
          const total = context.chart._metasets[0].total;
          const percent = (value / total) * 100;
          return `${percent.toFixed(1)}%`;
        },
      },
      title: {
        display: false, // ⛔ 제목은 수동으로 밖에 넣음
      },
    },
  };

  return (
    <div style={{ height: '460px', textAlign: 'left' }}>
      <h3 style={{ marginBottom: '40px',fontSize: '30px' }}>
        📦  제품별 매출 비중 (2014.12)
      </h3>
      <Pie data={chartData} options={options} />
    </div>
  );
}

export default PieChart;
