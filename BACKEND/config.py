import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# MongoDB 설정
MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_USERS = os.getenv("COLLECTION_USERS")
COLLECTION_EXPLAIN = os.getenv("COLLECTION_EXPLAIN")
COLLECTION_OUTLINE = os.getenv("COLLECTION_OUTLINE")
COLLECTION_INDUSTRY = os.getenv("COLLECTION_INDUSTRY")

# 서버 설정
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# 기타 설정
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
