from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import FRONTEND_URL

# 라우터 임포트
from routers import company, news, stock, investor

# FastAPI 앱 생성
app = FastAPI(
    title="투자 분석 API",
    description="기업 정보, 주가 데이터, 투자자 분석을 위한 REST API",
    version="2.0.0"
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(company.router, prefix="/api/v1")
app.include_router(news.router, prefix="/api/v1")
app.include_router(stock.router, prefix="/api/v1")
app.include_router(investor.router, prefix="/api/v1")

# 메인 페이지
@app.get("/")
async def root():
    return {
        "message": "✅ 투자 분석 API 서버 실행 중",
        "version": "2.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# 헬스 체크
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

# API 정보
@app.get("/api/info")
async def api_info():
    return {
        "name": "투자 분석 API",
        "version": "2.0.0",
        "endpoints": {
            "기업 정보": "/api/v1/company/*",
            "뉴스": "/api/v1/news/*",
            "주가 정보": "/api/v1/stock/*",
            "투자자 분석": "/api/v1/investor/*"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

