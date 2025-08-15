from pymongo import MongoClient
from config import MONGODB_URI, DB_NAME, COLLECTION_USERS, COLLECTION_EXPLAIN, COLLECTION_OUTLINE, COLLECTION_INDUSTRY

class DatabaseManager:
    def __init__(self):
        if not MONGODB_URI:
            raise ValueError("MONGODB_URI 환경변수가 설정되지 않았습니다.")
        
        self.client = MongoClient(MONGODB_URI)
        self.db = self.client[DB_NAME]
        
        # 컬렉션 초기화
        self.collection = self.db[COLLECTION_USERS]
        self.explain = self.db[COLLECTION_EXPLAIN]
        self.outline = self.db[COLLECTION_OUTLINE]
        self.industry = self.db[COLLECTION_INDUSTRY]
    
    def get_collection(self, collection_name: str):
        """컬렉션 이름으로 컬렉션 반환"""
        return self.db[collection_name]
    
    def close_connection(self):
        """데이터베이스 연결 종료"""
        self.client.close()

# 전역 데이터베이스 매니저 인스턴스
db_manager = DatabaseManager()
