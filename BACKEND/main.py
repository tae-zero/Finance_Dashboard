import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import company, news, stock, investor

app = FastAPI(
    title="Project 1 Backend API",
    description="기업 정보, 주가 데이터, 투자자 분석을 위한 REST API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(company.router, prefix="/api/v1")
app.include_router(news.router, prefix="/api/v1")
app.include_router(stock.router, prefix="/api/v1")
app.include_router(investor.router, prefix="/api/v1")

# 메인 페이지 (헬스체크용)
@app.get("/")
async def root():
    return {"message": "Project 1 Backend API", "status": "healthy", "port": os.getenv("PORT", "7000")}

# 헬스체크 엔드포인트
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

# API 정보
@app.get("/api/info")
async def api_info():
    return {
        "name": "Project 1 Backend API",
        "version": "1.0.0",
        "endpoints": {
            "기업 정보": "/api/v1/company/*",
            "뉴스": "/api/v1/news/*",
            "주가 정보": "/api/v1/stock/*",
            "투자자 분석": "/api/v1/investor/*"
        }
    }

if __name__ == "__main__":
    # Railway에서는 $PORT 환경변수를 사용하되, 7000으로 강제 설정
    port = int(os.getenv("PORT", 7000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"🚀 서버 시작 준비 중...")
    print(f"📍 호스트: {host}")
    print(f"🔌 포트: {port}")
    print(f"🌐 환경변수 PORT: {os.getenv('PORT')}")
    print(f"⚠️  포트 8080 충돌 방지를 위해 7000으로 설정")
    
    # 포트 8080이면 7000으로 강제 변경
    if port == 8080:
        port = 7000
        print(f"🔄 포트를 7000으로 변경했습니다.")
    
    try:
        uvicorn.run(app, host=host, port=port)
    except Exception as e:
        print(f"❌ 서버 시작 실패: {e}")
        raise e

