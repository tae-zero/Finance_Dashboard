'use client'

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';
import { API_ENDPOINTS } from '../config/api';
import api from '../config/api';

const industryList = [
  "IT 서비스", "건설", "기계·장비", "기타금융", "기타제조", "금속",
  "농업, 임업 및 어업", "보험", "비금속", "섬유·의류", "식음료·담배",
  "오락·문화", "운송·창고", "운송장비·부품", "유통", "의료·정밀기기",
  "은행", "제약", "종이·목재", "증권", "전기·가스", "전기·전자",
  "통신", "화학", "부동산", "일반 서비스"
];

function Sidebar() {
  const [searchTerm, setSearchTerm] = useState("");
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [companyList, setCompanyList] = useState<string[]>([]);
  const [isIndustryExpanded, setIsIndustryExpanded] = useState(true);
  const router = useRouter();
  const pathname = usePathname(); 

  useEffect(() => {
    api.get(API_ENDPOINTS.COMPANY_NAMES)
      .then(res => {
        if (Array.isArray(res.data)) {
          setCompanyList(res.data);
        } else {
          console.error("❌ 기업명 데이터가 배열이 아닙니다:", res.data);
          setCompanyList([]);
        }
      })
      .catch(err => console.error("기업명 불러오기 실패:", err));
  }, []);

  const handleSearch = (e: React.KeyboardEvent<HTMLInputElement> | React.MouseEvent<HTMLButtonElement>) => {
    if (e.type === 'keydown' && (e as React.KeyboardEvent).key !== 'Enter') return;
    
    const trimmed = searchTerm.trim();
    if (trimmed) {
      router.push(`/company/${encodeURIComponent(trimmed)}`);
      setSearchTerm("");
      setSuggestions([]);
      if (e.type === 'keydown') {
        (e.target as HTMLInputElement).blur();
      }
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearchTerm(value);

    if (value.trim() === "") {
      setSuggestions([]);
    } else {
      if (Array.isArray(companyList)) {
        const filtered = companyList.filter(name =>
          name.toLowerCase().includes(value.toLowerCase())
        );
        setSuggestions(filtered.slice(0, 10));
      } else {
        console.warn('⚠️ companyList가 배열이 아닙니다:', companyList);
        setSuggestions([]);
      }
    }
  };

  const handleIndustryClick = (industry: string) => {
    router.push(`/industry/${encodeURIComponent(industry)}`);
  };

  const handleTreasureHuntClick = () => {
    router.push('/treasure');
  };

  return (
    <aside className="w-80 h-screen bg-gradient-to-b from-slate-50 to-blue-50 border-r border-gray-200 shadow-lg overflow-y-auto">
      <div className="p-6">
        {/* 검색 섹션 */}
        <div className="mb-8">
          <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
            <span className="text-xl">🔍</span>
            검색
          </h3>
          <div className="relative">
            <input
              type="text"
              placeholder="종목명 검색"
              value={searchTerm}
              onChange={handleChange}
              onKeyDown={handleSearch}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl bg-white text-gray-700 focus:ring-4 focus:ring-blue-100 focus:border-blue-500 transition-all duration-200 font-medium"
            />
            <button 
              onClick={handleSearch}
              className="absolute right-2 top-1/2 transform -translate-y-1/2 px-4 py-2 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-lg hover:from-blue-600 hover:to-indigo-700 transition-all duration-200 font-medium"
            >
              검색
            </button>
          </div>
          
          {/* 검색 제안 */}
          {suggestions.length > 0 && (
            <ul className="mt-2 bg-white border-2 border-gray-200 rounded-xl shadow-lg max-h-48 overflow-y-auto">
              {suggestions.map((suggestion, index) => (
                <li key={index}>
                  <button
                    onClick={() => {
                      router.push(`/company/${encodeURIComponent(suggestion)}`);
                      setSearchTerm("");
                      setSuggestions([]);
                    }}
                    className="w-full px-4 py-3 text-left hover:bg-blue-50 transition-colors duration-200 text-gray-700 font-medium"
                  >
                    {suggestion}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* 산업별 보기 섹션 */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-gray-800 flex items-center gap-2">
              <span className="text-xl">🏭</span>
              산업별 보기
            </h3>
            <button
              onClick={() => setIsIndustryExpanded(!isIndustryExpanded)}
              className="text-gray-500 hover:text-gray-700 transition-colors"
            >
              {isIndustryExpanded ? '▼' : '▶'}
            </button>
          </div>

          {/* 보물찾기 버튼 */}
          <button
            onClick={handleTreasureHuntClick}
            className="w-full mb-4 px-4 py-3 bg-gradient-to-r from-yellow-400 to-orange-500 text-white font-bold rounded-xl hover:from-yellow-500 hover:to-orange-600 transform hover:scale-105 transition-all duration-200 shadow-lg"
          >
            💎 보물찾기 (저PBR/PER/대형주 필터링)
          </button>

          {/* 산업 목록 */}
          {isIndustryExpanded && (
            <div className="grid grid-cols-2 gap-2">
              {industryList.map((industry) => (
                <button
                  key={industry}
                  onClick={() => handleIndustryClick(industry)}
                  className="px-3 py-2 text-sm bg-white border-2 border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-all duration-200 text-gray-700 font-medium hover:shadow-md"
                >
                  {industry}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* 홈으로 버튼 */}
        <div className="mt-auto">
          <Link href="/">
            <button className="w-full px-4 py-3 bg-gradient-to-r from-blue-600 to-indigo-700 text-white font-bold rounded-xl hover:from-blue-700 hover:to-indigo-800 transform hover:scale-105 transition-all duration-200 shadow-lg flex items-center justify-center gap-2">
              <span className="text-lg">🏠</span>
              홈으로
            </button>
          </Link>
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;
