import os
import uvicorn
import time
from datetime import datetime, timedelta

def check_environment():
    """환경 체크"""
    try:
        # 필수 패키지 임포트 체크
        import pandas as pd
        import numpy as np
        import requests
        
        print("✅ 기본 패키지 확인 완료")
        
        # 환경변수 체크
        required_envs = ['MONGODB_URI', 'DB_NAME', 'PORT']
        missing_envs = [env for env in required_envs if not os.getenv(env)]
        
        if missing_envs:
            print(f"⚠️ 누락된 환경변수: {', '.join(missing_envs)}")
        else:
            print("✅ 환경변수 확인 완료")
            
    except ImportError as e:
        print(f"⚠️ 패키지 임포트 오류: {str(e)}")
    except Exception as e:
        print(f"⚠️ 환경 체크 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    print("🔄 서비스 초기화 중...")
    time.sleep(5)  # MongoDB 연결 대기
    
    # 환경 체크
    check_environment()
    
    # 서버 시작
    port = int(os.getenv("PORT", 7000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"🚀 서버 시작 준비 중...")
    print(f"📍 호스트: {host}")
    print(f"🔌 포트: {port}")
    
    uvicorn.run("main:app", host=host, port=port)