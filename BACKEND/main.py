# BACKEND/app/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import logging
from datetime import datetime
import traceback
import logging
logging.raiseExceptions = False
# =========================
# 로깅 설정 (환경변수 기반)
# =========================
APP_LOG_LEVEL = os.getenv("APP_LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, APP_LOG_LEVEL, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("api")

# noisy 서드파티 로거 억제 (Railway 로그 제한 회피)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.getLogger("yfinance").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

DEBUG = os.getenv("DEBUG", "false").lower() in ("1", "true", "yes")

def get_allowed_origins() -> list[str]:
    """환경변수 CORS_ORIGINS=comma,separated,urls 또는 기본값"""
    cors_env = os.getenv("CORS_ORIGINS", "").strip()
    if cors_env:
        return [o.strip() for o in cors_env.split(",") if o.strip()]
    # 기본 허용 오리진
    return [
        "https://finance-dashboard-git-main-jeongtaeyeongs-projects.vercel.app",
        "https://finance-dashboard.vercel.app",
        "https://finance-dashboard-db3g1y3vz-jeongtaeyeongs-projects.vercel.app",
        "http://localhost:3000",
    ]


def create_app() -> FastAPI:
    app = FastAPI(
        title="Project 1 Backend API",
        description="기업 정보, 주가 데이터, 투자자 분석을 위한 REST API",
        version="1.0.0",
    )

    allowed_origins = get_allowed_origins()
    logger.info("설정된 CORS Origins: %s", allowed_origins)

    # -------------------------------------------------
    # 표준 CORS 미들웨어만 사용 (커스텀 CORS 미들웨어 제거)
    # OPTIONS(Preflight) 자동 처리됨
    # -------------------------------------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=3600,
    )
    logger.info("CORS 미들웨어 설정 완료")

    # -------------------------------------------------
    # 전역 예외 핸들러: 최소 로그, DEBUG에서만 상세
    # -------------------------------------------------
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        # 필수 한 줄만 남기기
        logger.error("❌ 전역 에러: %s", str(exc))

        if DEBUG:
            # 개발환경에서만 상세 정보 남김
            logger.error("Traceback:\n%s", traceback.format_exc())
            logger.error(
                "요청 정보: method=%s path=%s query=%s",
                request.method,
                request.url.path,
                dict(request.query_params),
            )

        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "message": str(exc) if DEBUG else "An unexpected error occurred",
                "timestamp": datetime.now().isoformat(),
                "path": str(request.url),
            },
        )

    # -------------------------------------------------
    # 루트 & 헬스 체크 (가볍게)
    # -------------------------------------------------
    @app.get("/")
    async def root():
        if DEBUG:
            logger.info("📍 루트 엔드포인트 호출")
        return {
            "status": "healthy",
            "service": "Project 1 Backend API",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "environment": {
                "port": os.getenv("PORT", "7000"),
                "host": os.getenv("HOST", "0.0.0.0"),
                "railway_env": os.getenv("RAILWAY_ENVIRONMENT", "local"),
                "debug": DEBUG,
            },
        }

    @app.get("/health")
    @app.head("/health")
    async def health_check():
        # 헬스체크는 로그 최소화
        try:
            # DB 상태가 필요하면 여기에 가볍게 체크
            try:
                from utils.database import db_manager  # 선택적
                db_status = "connected" if db_manager.is_connected() else "disconnected"
            except Exception:
                db_status = "unknown"

            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "services": {"mongodb": db_status, "api": "running"},
            }
        except Exception as e:
            # 헬스체크 실패도 한 줄만
            logger.error("헬스체크 에러: %s", str(e))
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "timestamp": datetime.now().isoformat(),
                    "error": str(e) if DEBUG else "service unavailable",
                },
            )

    # -------------------------------------------------
    # 라우터 연결
    # -------------------------------------------------
    from routers import company, news, stock, investor
    app.include_router(company.router, prefix="/api/v1/company")
    app.include_router(news.router, prefix="/api/v1/news")
    app.include_router(stock.router, prefix="/api/v1/stock")
    app.include_router(investor.router, prefix="/api/v1/investor")

    # -------------------------------------------------
    # 데이터베이스 연결 (startup 이벤트)
    # -------------------------------------------------
    @app.on_event("startup")
    async def startup_event():
        try:
            from utils.database import db_manager
            await db_manager.connect()
            logger.info("✅ 데이터베이스 연결 완료")
        except Exception as e:
            logger.error("❌ 데이터베이스 연결 실패: %s", e)
            # 연결 실패해도 서버는 시작 (폴백 데이터 사용)

    logger.info("✅ 앱 초기화 완료")
    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "7000"))

    # access_log=False 로 접근 로그 억제 (Railway 로그량 절감)
    logger.info("🚀 서버 시작 - 호스트: %s, 포트: %s (log_level=%s)", host, port, APP_LOG_LEVEL)
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level=APP_LOG_LEVEL.lower(),
        access_log=False,
        proxy_headers=True,
    )
