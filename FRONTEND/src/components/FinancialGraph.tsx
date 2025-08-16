'use client'

import React from 'react';

interface FinancialGraphProps {
  companyName: string;
}

export default function FinancialGraph({ companyName }: FinancialGraphProps) {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">{companyName} 재무 현황</h3>
      <div className="space-y-4">
        {/* 매출액 */}
        <div className="p-4 bg-blue-50 rounded-lg">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700">매출액</span>
            <span className="text-sm text-gray-500">2024년</span>
          </div>
          <div className="text-2xl font-bold text-blue-600">2,450억원</div>
          <div className="text-sm text-green-600 mt-1">+12.5% vs 작년</div>
        </div>

        {/* 영업이익 */}
        <div className="p-4 bg-green-50 rounded-lg">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700">영업이익</span>
            <span className="text-sm text-gray-500">2024년</span>
          </div>
          <div className="text-2xl font-bold text-green-600">320억원</div>
          <div className="text-sm text-green-600 mt-1">+8.2% vs 작년</div>
        </div>

        {/* 순이익 */}
        <div className="p-4 bg-purple-50 rounded-lg">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700">순이익</span>
            <span className="text-sm text-gray-500">2024년</span>
          </div>
          <div className="text-2xl font-bold text-purple-600">280억원</div>
          <div className="text-sm text-green-600 mt-1">+15.3% vs 작년</div>
        </div>

        {/* 부채비율 */}
        <div className="p-4 bg-orange-50 rounded-lg">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700">부채비율</span>
            <span className="text-sm text-gray-500">2024년</span>
          </div>
          <div className="text-2xl font-bold text-orange-600">45.2%</div>
          <div className="text-sm text-red-600 mt-1">+2.1% vs 작년</div>
        </div>
      </div>
    </div>
  );
}
