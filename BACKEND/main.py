from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import logging
from datetime import datetime

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("api")

# CORS 허용 도메인
ALLOWED_ORIGINS = [
    "https://finance-dashboard-git-main-jeongtaeyeongs-projects.vercel.app",
    "https://finance-dashboard.vercel.app",
    "https://finance.taezero.com",
    "http://localhost:3000",
    "http://localhost:5173"
]

def create_app() -> FastAPI:
    app = FastAPI(
        title="Project 1 Backend API",
        description="기업 정보, 주가 데이터, 투자자 분석을 위한 REST API",
        version="1.0.0"
    )

    # CORS 미들웨어 설정
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=3600,
    )

    # 전역 예외 핸들러
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        error_msg = str(exc)
        logger.error(f"Global error: {error_msg}", exc_info=True)
        
        if "JSONDecodeError" in error_msg or "No timezone found" in error_msg:
            return JSONResponse(
                status_code=503,
                content={
                    "detail": "외부 서비스 일시적 오류",
                    "error": error_msg,
                    "timestamp": datetime.now().isoformat()
                }
            )
        
        return JSONResponse(
            status_code=500,
            content={
                "detail": "내부 서버 오류",
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }
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
        return {
            "message": "Project 1 Backend API",
            "status": "healthy",
            "port": os.getenv("PORT", "7000"),
            "timestamp": datetime.now().isoformat()
        }

    # 헬스체크 엔드포인트
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat()
        }

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 7000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"🚀 서버 시작 - 호스트: {host}, 포트: {port}")
    uvicorn.run(app, host=host, port=port, log_level="info")