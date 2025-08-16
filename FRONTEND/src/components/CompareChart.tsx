'use client'

import React from 'react';
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

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend);

interface CompareChartProps {
  metrics: { [key: string]: any };
  industryMetrics: { [key: string]: any };
  companyName: string;
  metricType: string;
}

const CompareChart = ({ metrics, industryMetrics, companyName, metricType }: CompareChartProps) => {
  // 🔍 디버깅 로그 추가
  console.log('🔍 CompareChart 렌더링 시작:', { metrics, industryMetrics, companyName, metricType });
  console.log('🔍 metrics 타입:', typeof metrics, Array.isArray(metrics));
  console.log('🔍 industryMetrics 타입:', typeof industryMetrics, Array.isArray(industryMetrics));
  
  // 데이터 유효성 검사
  if (!metrics || !industryMetrics) {
    console.log('❌ 데이터가 없음:', { metrics, industryMetrics });
    return <div>데이터를 불러오는 중...</div>;
  }

  // 단일 지표 데이터 추출
  const companyMetric = metrics[metricType];
  const industryMetric = industryMetrics[metricType];

  if (!companyMetric || !industryMetric) {
    console.log(`❌ ${metricType} 데이터가 없음:`, { companyMetric, industryMetric });
    return <div>{metricType} 데이터를 불러오는 중...</div>;
  }

  const years = Object.keys(companyMetric || {});
  const companyValues = Object.values(companyMetric || {});
  const industryValues = Object.values(industryMetric || {});

  console.log(`🔍 ${metricType} 차트 데이터:`, { years, companyValues, industryValues });

  return (
    <div style={{ maxWidth: '600px', margin: '40px auto' }}>
      <h4 style={{fontSize: '25px'}}>{metricType} 추이</h4>
      <Line
        data={{
          labels: years,
          datasets: [
            {
              label: `${companyName}`,
              data: companyValues,
              borderColor: 'blue',
              backgroundColor: 'rgba(0,0,255,0.1)',
              tension: 0.3,
              pointRadius: 0,
              pointHoverRadius: 0,
              borderWidth: 2,
            },
            {
              label: `코스피 기준 업종 평균`,
              data: industryValues,
              borderColor: 'orange',
              backgroundColor: 'rgba(255,165,0,0.1)',
              tension: 0.3,
              pointRadius: 0,
              pointHoverRadius: 0,
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
                label: (ctx: any) => `${ctx.dataset.label}: ${ctx.parsed.y.toFixed(2)}`
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
  );
};

export default CompareChart;
