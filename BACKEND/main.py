from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import os
import logging
from datetime import datetime
import traceback

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("api")

def create_app() -> FastAPI:
    app = FastAPI(
        title="Project 1 Backend API",
        description="기업 정보, 주가 데이터, 투자자 분석을 위한 REST API",
        version="1.0.0"
    )

    # CORS 설정
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 개발 중에는 모든 origin 허용
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=3600,
    )

    # 신뢰할 수 있는 호스트 설정
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # 개발 중에는 모든 호스트 허용
    )

    # 전역 예외 핸들러
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        error_msg = str(exc)
        logger.error(f"Global error: {error_msg}")
        logger.error(traceback.format_exc())
        
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "message": error_msg,
                "timestamp": datetime.now().isoformat(),
                "path": str(request.url)
            }
        )

    # 메인 페이지 (헬스체크용)
    @app.get("/")
    async def root():
        try:
            return {
                "status": "healthy",
                "service": "Project 1 Backend API",
                "version": "1.0.0",
                "timestamp": datetime.now().isoformat(),
                "environment": {
                    "port": os.getenv("PORT", "7000"),
                    "host": os.getenv("HOST", "0.0.0.0")
                },
                "endpoints": {
                    "health": "/health",
                    "api_info": "/api/info",
                    "docs": "/docs",
                    "redoc": "/redoc"
                }
            }
        except Exception as e:
            logger.error(f"Root endpoint error: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail=str(e))

    # 헬스체크 엔드포인트
    @app.get("/health")
    async def health_check():
        try:
            # MongoDB 연결 체크
            from utils.database import db_manager
            db_status = "connected" if db_manager.is_connected() else "disconnected"
            
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "services": {
                    "mongodb": db_status,
                    "api": "running"
                }
            }
        except Exception as e:
            logger.error(f"Health check error: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }

    # API 정보
    @app.get("/api/info")
    async def api_info():
        return {
            "name": "Project 1 Backend API",
            "version": "1.0.0",
            "description": "기업 정보, 주가 데이터, 투자자 분석을 위한 REST API",
            "endpoints": {
                "company": "/api/v1/company/*",
                "news": "/api/v1/news/*",
                "stock": "/api/v1/stock/*",
                "investor": "/api/v1/investor/*"
            }
        }

    # 라우터 등록
    from routers import company, news, stock, investor
    
    app.include_router(company.router, prefix="/api/v1")
    app.include_router(news.router, prefix="/api/v1")
    app.include_router(stock.router, prefix="/api/v1")
    app.include_router(investor.router, prefix="/api/v1")

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 7000))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(app, host=host, port=port, log_level="info")