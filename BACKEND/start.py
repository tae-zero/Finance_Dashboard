import os
import uvicorn

if __name__ == "__main__":
    port = int(os.getenv("PORT", 7000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"🚀 서버 시작 준비 중...")
    print(f"📍 호스트: {host}")
    print(f"🔌 포트: {port}")
    
    uvicorn.run("main:app", host=host, port=port)
