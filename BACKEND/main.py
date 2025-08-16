from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

app = FastAPI(
    title="Project 1 Backend API",
    description="기업 정보, 주가 데이터, 투자자 분석을 위한 REST API",
    version="1.0.0"
)

# CORS 설정
ALLOWED_ORIGINS = [
    "https://finance-dashboard-git-main-jeongtaeyeongs-projects.vercel.app",
    "https://finance-dashboard.vercel.app",
    "https://finance.taezero.com",
    "http://localhost:3000",
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600
)

# 전역 예외 핸들러
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )

# 라우터 등록
from routers import company, news, stock, investor

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

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 7000))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(app, host=host, port=port)