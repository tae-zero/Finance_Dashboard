from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import logging
import json
from datetime import datetime
import traceback

# 로깅 설정
logging.basicConfig(
    level=logging.DEBUG,  # DEBUG 레벨로 변경하여 더 상세한 로그 확인
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("api")

def log_request_details(request: Request):
    """요청 상세 정보 로깅"""
    return {
        "method": request.method,
        "url": str(request.url),
        "headers": dict(request.headers),
        "client_host": request.client.host if request.client else None,
        "path_params": request.path_params,
        "query_params": str(request.query_params),
    }

def create_app() -> FastAPI:
    app = FastAPI(
        title="Project 1 Backend API",
        description="기업 정보, 주가 데이터, 투자자 분석을 위한 REST API",
        version="1.0.0"
    )

    # CORS 설정
    ALLOWED_ORIGINS = [
        "https://finance-dashboard-git-main-jeongtaeyeongs-projects.vercel.app",
        "https://finance-dashboard.vercel.app",
        "http://localhost:3000",
    ]
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

    @app.middleware("http")
    async def cors_debug_middleware(request: Request, call_next):
        """CORS 디버깅을 위한 미들웨어"""
        # 요청 정보 로깅
        req_details = log_request_details(request)
        logger.debug(f"➡️ 수신된 요청 상세 정보: {json.dumps(req_details, indent=2, ensure_ascii=False)}")

        # Origin 헤더 체크
        origin = request.headers.get("origin")
        if origin:
            logger.info(f"🌐 요청 Origin: {origin}")
            if origin not in ALLOWED_ORIGINS:
                logger.warning(f"⚠️ 허용되지 않은 Origin: {origin}")
        else:
            logger.info("❓ Origin 헤더 없음")

        # preflight 요청 체크
        if request.method == "OPTIONS":
            logger.info("🔍 Preflight 요청 감지")
            logger.debug(f"Preflight 요청 헤더: {dict(request.headers)}")

        try:
            # 응답 처리
            response = await call_next(request)
            
            # 응답 헤더 로깅
            cors_headers = {k: v for k, v in response.headers.items() if k.lower().startswith('access-control')}
            logger.debug(f"📤 응답 CORS 헤더: {json.dumps(cors_headers, indent=2)}")
            
            # 상태 코드 로깅
            logger.info(f"📊 응답 상태 코드: {response.status_code}")
            
            return response

        except Exception as e:
            logger.error(f"❌ 요청 처리 중 오류 발생: {str(e)}")
            logger.error(traceback.format_exc())
            return JSONResponse(
                status_code=500,
                content={"detail": str(e)},
                headers={
                    "Access-Control-Allow-Origin": origin or "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
                    "Access-Control-Allow-Headers": "*",
                    "Access-Control-Max-Age": "3600"
                }
            )

    @app.options("/{rest_of_path:path}")
    async def preflight_handler(request: Request):
        """Preflight 요청 처리"""
        logger.info(f"🔄 Preflight 요청 처리: {request.url}")
        origin = request.headers.get("origin")
        
        if origin and origin not in ALLOWED_ORIGINS:
            logger.warning(f"⚠️ Preflight: 허용되지 않은 Origin ({origin})")
            return JSONResponse(
                content={"detail": "Not allowed origin"},
                status_code=403
            )
            
        logger.info(f"✅ Preflight 요청 허용 (Origin: {origin})")
        return JSONResponse(
            content={},
            headers={
                "Access-Control-Allow-Origin": origin,
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Max-Age": "3600"
            }
        )

    # 전역 예외 핸들러
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        error_msg = str(exc)
        logger.error(f"❌ 전역 에러: {error_msg}")
        logger.error(traceback.format_exc())
        
        # 요청 정보 로깅
        logger.error(f"에러 발생 요청 정보: {log_request_details(request)}")
        
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
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Max-Age": "3600"
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