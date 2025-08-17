'use client'

import React, { useEffect, useState } from 'react';
import { API_ENDPOINTS } from '../config/api';
import api from '../config/api';

interface SalesRow {
  사업부문: string;
  매출유형?: string;  // CSV 데이터용 (선택적)
  매출품목명: string;
  구분: string;
  '2022_12 매출액': string | number;
  '2023_12 매출액': string | number;
  '2024_12 매출액': string | number;
}

interface SalesTableProps {
  name: string;
}

function SalesTable({ name }: SalesTableProps) {
  const [rows, setRows] = useState<SalesRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    const fetchSalesData = async () => {
      try {
        setLoading(true);
        // 백엔드 API를 통해 매출 데이터 가져오기
        const response = await api.get(API_ENDPOINTS.SALES_DATA);
        if (response.data && response.data[name]) {
          setRows(response.data[name]);
        } else {
          // 폴백: 정적 파일 시도
          const staticResponse = await fetch('/매출비중_chartjs_데이터.json');
          const staticData = await staticResponse.json();
          if (staticData[name]) {
            setRows(staticData[name]);
          } else {
            setError(true);
          }
        }
      } catch (err) {
        console.error("매출 데이터 로드 실패:", err);
        // 폴백: 정적 파일 시도
        try {
          const staticResponse = await fetch('/매출비중_chartjs_데이터.json');
          const staticData = await staticResponse.json();
          if (staticData[name]) {
            setRows(staticData[name]);
          } else {
            setError(true);
          }
        } catch (staticErr) {
          console.error("정적 파일 폴백 실패:", staticErr);
          setError(true);
        }
      } finally {
        setLoading(false);
      }
    };

    if (name) {
      fetchSalesData();
    }
  }, [name]);

  if (loading) {
    return (
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500 mx-auto mb-4"></div>
        <p>📉 매출 데이터를 불러오는 중입니다...</p>
      </div>
    );
  }

  if (error || rows.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p>📉 매출 데이터를 불러올 수 없습니다.</p>
        <p className="text-sm">데이터가 준비되지 않았거나 일시적인 오류가 발생했습니다.</p>
      </div>
    );
  }

  const tooltipMap: { [key: string]: string } = {
    '내수': '국내에서 발생한 매출이야.',
    '수출': '해외 수출을 통해 얻은 매출이야.',
    '로컬': '지역 사업장에서 발생한 매출이야.',
    '미분류': '구체적인 구분 없이 집계된 매출이야.',
    '비중': '전체 매출에서 이 부문이 차지하는 비율이야.'
  };

  const grouped = rows.reduce((acc: { [key: string]: SalesRow[] }, row) => {
    const key = `${row['사업부문']} | ${row['매출품목명']}`;
    if (!acc[key]) acc[key] = [];
    acc[key].push(row);
    return acc;
  }, {});

  // CSV 상세 데이터 가져오기
  const [csvData, setCsvData] = useState<SalesRow[]>([]);
  const [showCsvData, setShowCsvData] = useState(false);
  const [csvLoading, setCsvLoading] = useState(false);

  const fetchCsvData = async () => {
    try {
      setCsvLoading(true);
      const response = await api.get(`/company/${name}/sales-composition`);
      if (response.data && response.data.data) {
        setCsvData(response.data.data);
        setShowCsvData(true);
      }
    } catch (err) {
      console.error("CSV 데이터 로드 실패:", err);
    } finally {
      setCsvLoading(false);
    }
  };

  const renderValue = (val: string | number) => {
    if (typeof val === 'string' && val.includes('%')) return val;
    const num = Number(val);
    return isNaN(num) ? '-' : num.toLocaleString();
  };

  const borderStyle = {
    border: '2px solid black',
    textAlign: 'center' as const,
    whiteSpace: 'nowrap' as const
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-xl font-bold text-gray-800">💰 사업부문별 매출액 (단위: 백만원)</h3>
        <button
          onClick={fetchCsvData}
          disabled={csvLoading}
          className="bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg transition-colors duration-200 flex items-center gap-2"
        >
          {csvLoading ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              로딩중...
            </>
          ) : (
            <>
              📊 보기 ▼
            </>
          )}
        </button>
      </div>
      {Object.entries(grouped).map(([groupKey, items], idx) => (
        <div key={idx} style={{ marginBottom: '30px' }}>
          <h4 style={{ margin: '10px 0', fontSize: '16px', fontWeight: 'bold' }}>{groupKey}</h4>
          <table style={{
            borderCollapse: 'collapse',
            width: '100%',
            border: '2px solid black'
          }}>
            <thead>
              <tr>
                <th style={borderStyle}>구분</th>
                <th style={borderStyle}>2022/12</th>
                <th style={borderStyle}>2023/12</th>
                <th style={borderStyle}>2024/12</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item, i) => (
                <tr key={i} style={borderStyle}>
                  <td style={borderStyle} title={tooltipMap[item['구분']] || ''}>{item['구분']}</td>
                  <td style={borderStyle}>{renderValue(item['2022_12 매출액'])}</td>
                  <td style={borderStyle}>{renderValue(item['2023_12 매출액'])}</td>
                  <td style={borderStyle}>{renderValue(item['2024_12 매출액'])}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ))}

      {/* CSV 상세 데이터 표시 */}
      {showCsvData && csvData.length > 0 && (
        <div className="mt-8 p-6 bg-gray-50 rounded-xl border-2 border-gray-200">
          <h4 className="text-lg font-bold text-gray-800 mb-4">📋 {name} 매출 구성 상세 데이터 (CSV)</h4>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse border border-gray-300">
              <thead>
                <tr className="bg-gray-100">
                  <th className="border border-gray-300 px-3 py-2 text-left">사업부문</th>
                  <th className="border border-gray-300 px-3 py-2 text-left">매출유형</th>
                  <th className="border border-gray-300 px-3 py-2 text-left">매출품목명</th>
                  <th className="border border-gray-300 px-3 py-2 text-left">구분</th>
                  <th className="border border-gray-300 px-3 py-2 text-right">2022/12</th>
                  <th className="border border-gray-300 px-3 py-2 text-right">2023/12</th>
                  <th className="border border-gray-300 px-3 py-2 text-right">2024/12</th>
                </tr>
              </thead>
              <tbody>
                {csvData.map((row, idx) => (
                  <tr key={idx} className="hover:bg-gray-50">
                    <td className="border border-gray-300 px-3 py-2">{row.사업부문}</td>
                    <td className="border border-gray-300 px-3 py-2">{row.매출유형}</td>
                    <td className="border border-gray-300 px-3 py-2">{row.매출품목명}</td>
                    <td className="border border-gray-300 px-3 py-2">{row.구분}</td>
                    <td className="border border-gray-300 px-3 py-2 text-right">{renderValue(row['2022_12 매출액'])}</td>
                    <td className="border border-gray-300 px-3 py-2 text-right">{renderValue(row['2023_12 매출액'])}</td>
                    <td className="border border-gray-300 px-3 py-2 text-right">{renderValue(row['2024_12 매출액'])}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

export default SalesTable;
