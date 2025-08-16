import os
from pymongo import MongoClient
from typing import Optional

class DatabaseManager:
    def __init__(self):
        # MongoDB 연결 문자열 가져오기
        mongodb_uri = os.getenv("MONGODB_URI")
        if not mongodb_uri:
            raise ValueError("MONGODB_URI 환경변수가 설정되지 않았습니다.")
        
        # 데이터베이스 이름 가져오기
        db_name = os.getenv("DB_NAME", "testDB")
        if not isinstance(db_name, str):
            raise ValueError("DB_NAME 환경변수가 문자열이어야 합니다.")
        
        try:
            # MongoDB 클라이언트 연결
            self.client = MongoClient(mongodb_uri)
            
            # 연결 테스트
            self.client.admin.command('ping')
            print("✅ MongoDB 연결 성공!")
            
            # 데이터베이스 선택
            self.db = self.client[db_name]
            print(f"✅ 데이터베이스 '{db_name}' 선택됨")
            
        except Exception as e:
            print(f"❌ MongoDB 연결 실패: {e}")
            raise e
    
    def get_collection(self, collection_name: str):
        """컬렉션 가져오기"""
        return self.db[collection_name]
    
    def close_connection(self):
        """연결 종료"""
        if hasattr(self, 'client'):
            self.client.close()
            print(" MongoDB 연결 종료")

# 전역 인스턴스 생성
try:
    db_manager = DatabaseManager()
except Exception as e:
    print(f"⚠️ 데이터베이스 매니저 초기화 실패: {e}")
    db_manager = None
