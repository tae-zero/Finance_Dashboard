'use client'

import { useState, useEffect } from 'react'
import Dashboard from '@/components/Dashboard'
import GuidePopup from '@/components/GuidePopup'

export default function Home() {
  const [showGuide, setShowGuide] = useState(true)

  return (
    <div className="min-h-screen bg-gray-50">
                        {/* 헤더 */}
                  <header className="bg-white shadow-sm border-b border-gray-200">
                    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                      <div className="flex items-center justify-center h-16 relative">
                        {/* 중앙: 제목 */}
                        <div className="text-center">
                          <h1 className="text-2xl font-bold text-blue-600">주린이 놀이터</h1>
                          <p className="text-gray-600"></p>
                        </div>
                        
                        {/* 오른쪽: 가이드 버튼 */}
                        <button
                          onClick={() => setShowGuide(!showGuide)}
                          className="absolute right-0 p-2 text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-md transition-colors"
                          title="사이트 이용 가이드"
                        >
                          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                        </button>
                      </div>
                    </div>
                  </header>

      {/* 메인 대시보드 */}
      <Dashboard />

      {/* 가이드 팝업 */}
      <GuidePopup open={showGuide} onClose={() => setShowGuide(false)} />
    </div>
  )
}
