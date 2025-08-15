import React, { useState } from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route
} from 'react-router-dom';
import IndustryAnalysis from './industryAnalysis.jsx';
import Dashboard from './Dashboard';
import CompanyDetail from './CompanyDetail';
import TreasureHunt from './TreasureHunt';
import Sidebar from './Sidebar.jsx';
import GuidePopup from './GuidePopup.jsx';
import { useTooltip, TooltipImage } from './utils/tooltip.jsx';

function App() {
  const [showGuide, setShowGuide] = useState(false);
  const { showTooltip, tooltipPosition, handleMouseEnter, handleMouseMove, handleMouseLeave } = useTooltip();

  return (

    <Router>
    <div className="app-layout">
      {/* ✅ 전체 콘텐츠: 사이드바 + 본문 + 배너 포함 */}
      <div style={{ display: 'flex' }}>
        
        {/* ✅ 사이드바: 왼쪽 고정 */}
        <div style={{ position: 'fixed', top: 0, left: 0, height: '100vh', zIndex: 99 }}>
          <Sidebar />
        </div>

        {/* ✅ 본문 콘텐츠 + 배너 */}
        <div style={{ marginLeft: '260px', flex: 1 }}>
          
          {/* ✅ 이 안에만 배너 표시 */}
          <header className="page-header-banner">
            <div className="inner">
              <div className="banner-texts">
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                <h1 style={{ display: 'inline-block' }}
                onMouseEnter={handleMouseEnter}
                onMouseMove={handleMouseMove}
                onMouseLeave={handleMouseLeave}>🎡</h1>
                <h1 style={{ display: 'inline-block' }}>주린이 놀이터</h1>
                <h1
                  style={{ display: 'inline-block' }}
                  onMouseEnter={handleMouseEnter}
                  onMouseMove={handleMouseMove}
                  onMouseLeave={handleMouseLeave}
                >
                  🎡
                </h1>
              </div>
                <h2>주린이를 위한 친절한 주식투자 대시보드</h2>
                  <TooltipImage 
                    show={showTooltip}
                    position={tooltipPosition}
                    imageSrc="/투자는신중하게.jpg"
                    alt="투자 가이드"
                  />
              </div>
              <button
                onClick={() => setShowGuide(true)}
                className="guide-button"
              >
                사이트 사용 가이드
              </button>
              <GuidePopup open={showGuide} onClose={() => setShowGuide(false)} />
            </div>
          </header>

          {/* ✅ 본문 */}
          <main className="dashboard-container" style={{ flex: 1, padding: '20px'  }}>
            <div className="content-wrapper">
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/company/:name" element={<CompanyDetail />} />
                <Route path="/industry/:industry" element={<IndustryAnalysis />} />
                <Route path="treasure" element={<TreasureHunt />} />
              </Routes>
            </div>
          </main>
        </div>
      </div>
    </div>
    </Router>

  );
}

export default App;
