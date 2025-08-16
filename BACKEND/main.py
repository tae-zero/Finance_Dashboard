import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routers import company, news, stock, investor

app = FastAPI(
    title="Project 1 Backend API",
    description="기업 정보, 주가 데이터, 투자자 분석을 위한 REST API",
    version="1.0.0"
)

# CORS 설정
origins = [
    "https://finance-dashboard-git-main-jeongtaeyeongs-projects.vercel.app",
    "http://localhost:3000",
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600
)

# 전역 CORS 미들웨어
@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

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
    import uvicorn
    port = int(os.getenv("PORT", 7000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"🚀 서버 시작 준비 중...")
    print(f"📍 호스트: {host}")
    print(f"🔌 포트: {port}")
    
    uvicorn.run(app, host=host, port=port)