from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import logging
from datetime import datetime
import traceback
import json

# 로깅 설정
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("api")

def get_allowed_origins():
    """환경변수에서 CORS Origins 가져오기"""
    cors_origins = os.getenv("CORS_ORIGINS", "")
    if not cors_origins:
        # 기본값 설정
        return [
            "https://finance-dashboard-git-main-jeongtaeyeongs-projects.vercel.app",
            "https://finance-dashboard.vercel.app",
            "http://localhost:3000"
        ]
    return [origin.strip() for origin in cors_origins.split(",")]

def log_request_details(request: Request) -> dict:
    """요청 정보를 로그에 포함하기 위해 상세 정보를 추출합니다."""
    return {
        "method": request.method,
        "url": str(request.url),
        "path": request.url.path,
        "query_params": dict(request.query_params),
        "headers": dict(request.headers),
        "timestamp": datetime.now().isoformat()
    }

def create_app() -> FastAPI:
    app = FastAPI(
        title="Project 1 Backend API",
        description="기업 정보, 주가 데이터, 투자자 분석을 위한 REST API",
        version="1.0.0"
    )

    ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(',')
    logger.info(f"설정된 CORS Origins: {ALLOWED_ORIGINS}")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=3600,
    )
    logger.info("CORS 미들웨어 설정 완료")

    @app.middleware("http")
    async def cors_debug_middleware(request: Request, call_next):
        # 로그 레벨을 최소화하여 Railway 제한 방지
        origin = request.headers.get("origin")
        
        # CORS 검사만 수행하고 로그는 최소화
        if origin and origin not in ALLOWED_ORIGINS:
            logger.warning(f"⚠️ 허용되지 않은 Origin: {origin}")

        try:
            response = await call_next(request)
            
            # CORS 헤더 설정 (로그 없이)
            response.headers["Access-Control-Allow-Origin"] = origin if origin and origin in ALLOWED_ORIGINS else "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
            response.headers["Access-Control-Allow-Headers"] = "*"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Max-Age"] = "3600"
            
            return response

        except Exception as e:
            logger.error(f"❌ 요청 처리 중 오류 발생: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"detail": str(e)},
                headers={
                    "Access-Control-Allow-Origin": origin if origin and origin in ALLOWED_ORIGINS else "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
                    "Access-Control-Allow-Headers": "*",
                    "Access-Control-Allow-Credentials": "true",
                    "Access-Control-Max-Age": "3600"
                }
            )

    @app.options("/{rest_of_path:path}")
    async def preflight_handler(request: Request):
        logger.debug(f"🔄 Preflight 요청 처리: {request.url}")
        origin = request.headers.get("origin")
        
        if origin and origin not in ALLOWED_ORIGINS:
            logger.warning(f"⚠️ Preflight: 허용되지 않은 Origin ({origin})")
            return JSONResponse(
                content={"detail": "Not allowed origin"},
                status_code=403,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
                    "Access-Control-Allow-Headers": "*",
                    "Access-Control-Allow-Credentials": "true",
                    "Access-Control-Max-Age": "3600"
                }
            )
            
        logger.debug(f"✅ Preflight 요청 허용 (Origin: {origin})")
        return JSONResponse(
            content={},
            headers={
                "Access-Control-Allow-Origin": origin if origin else "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Max-Age": "3600"
            }
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        error_msg = str(exc)
        logger.error("❌ 전역 에러: %s", error_msg)
        logger.error(traceback.format_exc())
        logger.error("에러 발생 요청 정보: %s", log_request_details(request))
        
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "message": error_msg,
                "timestamp": datetime.now().isoformat(),
                "path": str(request.url)
            },
            headers={
                "Access-Control-Allow-Origin": request.headers.get("origin", "*"),
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Max-Age": "3600"
            }
        )

    @app.get("/")
    async def root():
        logger.info("📍 루트 엔드포인트 호출")
        return {
            "status": "healthy",
            "service": "Project 1 Backend API",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "environment": {
                "port": os.getenv("PORT", "7000"),
                "host": os.getenv("HOST", "0.0.0.0"),
                "railway_env": os.getenv("RAILWAY_ENVIRONMENT", "local")
            }
        }

    @app.get("/health")
    @app.head("/health")
    async def health_check():
        logger.debug("🏥 헬스체크 엔드포인트 호출")
        try:
            from utils.database import db_manager
            db_status = "connected" if db_manager.is_connected() else "disconnected"
            
            response = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "services": {
                    "mongodb": db_status,
                    "api": "running"
                }
            }
            logger.debug(f"헬스체크 응답: {response}")
            return response
        except Exception as e:
            logger.error(f"헬스체크 에러: {str(e)}")
            logger.error(traceback.format_exc())
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "timestamp": datetime.now().isoformat(),
                    "error": str(e)
                }
            )

    from routers import company, news, stock, investor
    app.include_router(company.router, prefix="/api/v1")
    app.include_router(news.router, prefix="/api/v1")
    app.include_router(stock.router, prefix="/api/v1")
    app.include_router(investor.router, prefix="/api/v1")

    logger.info("✅ 앱 초기화 완료")
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    # 포트를 강제로 7000으로 설정
    port = 7000
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"🚀 서버 시작 - 호스트: {host}, 포트: {port}")
    logger.info(f"⚠️ 환경변수 PORT 무시하고 강제로 7000 사용")
    uvicorn.run(app, host=host, port=port, log_level="debug")