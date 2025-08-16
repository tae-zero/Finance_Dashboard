import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import company, news, stock, investor

app = FastAPI()

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

# 메인 페이지
@app.get("/")
async def root():
    return {"message": "Project 1 Backend API"}

if __name__ == "__main__":
    # 7000대 포트 사용 (기존 8000대와 충돌 방지)
    port = int(os.getenv("PORT", 7000))
    print(f"🚀 서버 시작: 0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)

