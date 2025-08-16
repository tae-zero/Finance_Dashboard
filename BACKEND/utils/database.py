from pymongo import MongoClient
import os
import logging
from typing import Optional

logger = logging.getLogger("database")

class DatabaseManager:
    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.db = None
        self._connected = False
        self.connect()

    def connect(self):
        """MongoDB 연결"""
        try:
            mongodb_uri = os.getenv("MONGODB_URI")
            if not mongodb_uri:
                raise ValueError("MONGODB_URI 환경변수가 설정되지 않았습니다.")

            self.client = MongoClient(mongodb_uri)
            db_name = os.getenv("DB_NAME", "testDB")
            self.db = self.client[db_name]
            
            # 연결 테스트
            self.client.admin.command('ping')
            self._connected = True
            logger.info("✅ MongoDB 연결 성공!")
            logger.info(f"✅ 데이터베이스 '{db_name}' 선택됨")
            
        except Exception as e:
            logger.error(f"MongoDB 연결 실패: {str(e)}")
            self._connected = False
            raise

    def is_connected(self) -> bool:
        """연결 상태 확인"""
        return self._connected and self.client is not None and self.db is not None

    def get_database(self):
        """데이터베이스 객체 반환"""
        if not self.is_connected():
            self.connect()
        return self.db

    def get_collection(self, collection_name: str):
        """컬렉션 객체 반환"""
        if not self.is_connected():
            self.connect()
        return self.db[collection_name]

    def close(self):
        """MongoDB 연결 종료"""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
            self._connected = False

    def __del__(self):
        """소멸자에서 연결 정리"""
        self.close()

# 싱글톤 인스턴스 생성
db_manager = DatabaseManager()