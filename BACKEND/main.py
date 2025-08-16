from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import logging
from datetime import datetime
import traceback

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

def create_app() -> FastAPI:
    app = FastAPI(
        title="Project 1 Backend API",
        description="기업 정보, 주가 데이터, 투자자 분석을 위한 REST API",
        version="1.0.0"
    )

    # CORS 설정
    allowed_origins = get_allowed_origins()
    logger.info(f"설정된 CORS Origins: {allowed_origins}")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=3600,
    )

    # 요청/응답 로깅 및 CORS 헤더 강제 설정 미들웨어
    @app.middleware("http")
    async def cors_force_middleware(request: Request, call_next):
        # 요청 로깅
        logger.info(f"➡️ 요청: {request.method} {request.url}")
        logger.debug(f"요청 헤더: {dict(request.headers)}")
        
        # Origin 헤더 체크
        origin = request.headers.get("origin")
        if origin:
            logger.info(f"🌐 요청 Origin: {origin}")
            if origin not in allowed_origins:
                logger.warning(f"⚠️ 허용되지 않은 Origin: {origin}")
        
        # 응답 처리
        response = await call_next(request)
        
        # 응답 로깅
        logger.info(f"⬅️ 응답 상태 코드: {response.status_code}")
        logger.debug(f"응답 헤더: {dict(response.headers)}")
        
        # CORS 헤더 강제 설정
        if origin and origin in allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            logger.debug(f"✅ CORS 헤더 설정: {origin}")
        else:
            response.headers["Access-Control-Allow-Origin"] = "*"
            logger.debug("✅ CORS 헤더 설정: *")
        
        # 추가 CORS 헤더 설정
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Max-Age"] = "3600"
        
        return response

    # OPTIONS 요청 (preflight) 명시적 처리
    @app.options("/{rest_of_path:path}")
    async def preflight_handler(request: Request):
        logger.info(f"🔄 Preflight 요청 처리: {request.url}")
        origin = request.headers.get("origin")
        
        if origin and origin not in allowed_origins:
            logger.warning(f"⚠️ Preflight: 허용되지 않은 Origin ({origin})")
            return JSONResponse(
                content={"detail": "Not allowed origin"},
                status_code=403,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
                    "Access-Control-Allow-Headers": "*",
                    "Access-Control-Max-Age": "3600"
                }
            )
            
        logger.info(f"✅ Preflight 요청 허용 (Origin: {origin})")
        return JSONResponse(
            content={},
            headers={
                "Access-Control-Allow-Origin": origin if origin else "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Max-Age": "3600"
            }
        )

    # 전역 예외 핸들러
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        error_msg = str(exc)
        logger.error(f"❌ 전역 에러: {error_msg}")
        logger.error(traceback.format_exc())
        
        origin = request.headers.get("origin")
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "message": error_msg,
                "timestamp": datetime.now().isoformat(),
                "path": str(request.url)
            },
            headers={
                "Access-Control-Allow-Origin": origin if origin in allowed_origins else "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Max-Age": "3600"
            }
        )

    # 메인 페이지 (헬스체크용)
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

    # 헬스체크 엔드포인트
    @app.get("/health")
    @app.head("/health")
    async def health_check():
        logger.info("🏥 헬스체크 엔드포인트 호출")
        try:
            # MongoDB 연결 체크
            from utils.database import db_manager
            db_status = "connected" if db_manager.is_connected() else "disconnected"
            
            response = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "services": {
                    "mongodb": db_status,
                    "api": "running"
                },
                "environment": {
                    "railway": os.getenv("RAILWAY_ENVIRONMENT", "local"),
                    "cors_origins": allowed_origins
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

    # 라우터 등록
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
    port = int(os.getenv("PORT", 7000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"🚀 서버 시작 - 호스트: {host}, 포트: {port}")
    uvicorn.run(app, host=host, port=port, log_level="debug")