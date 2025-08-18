#!/bin/bash

echo "🚀 Finance Dashboard 개발 환경 설정 시작..."

# 1. 의존성 설치
echo "📦 의존성 설치 중..."
cd FRONTEND && npm install && cd ..
cd BACKEND && pip install -r requirements.txt && cd ..

# 2. 환경변수 파일 생성
echo "⚙️ 환경변수 파일 생성 중..."
if [ ! -f "FRONTEND/.env.local" ]; then
    cat > FRONTEND/.env.local << EOF
# 로컬 개발 환경
NODE_ENV=development
NEXT_PUBLIC_API_BASE_URL=http://localhost:7000/api/v1
NEXT_PUBLIC_ENVIRONMENT=local
NEXT_PUBLIC_APP_NAME=주린이 놀이터 (개발)
EOF
    echo "✅ FRONTEND/.env.local 생성 완료"
fi

# 3. PWA 아이콘 생성 (기본)
echo "🎨 PWA 아이콘 생성 중..."
if [ ! -f "FRONTEND/public/icon-192x192.png" ]; then
    echo "⚠️ PWA 아이콘 파일이 없습니다. 수동으로 생성해주세요."
fi

# 4. 개발 서버 시작
echo "🌐 개발 서버 시작 중..."
echo "백엔드 서버: http://localhost:7000"
echo "프론트엔드 서버: http://localhost:3000"

# 백그라운드에서 백엔드 서버 시작
cd BACKEND && python main.py &
BACKEND_PID=$!

# 백엔드 서버 시작 대기
sleep 5

# 프론트엔드 서버 시작
cd ../FRONTEND && npm run dev &
FRONTEND_PID=$!

echo "✅ 개발 환경 설정 완료!"
echo "백엔드 PID: $BACKEND_PID"
echo "프론트엔드 PID: $FRONTEND_PID"
echo ""
echo "서버 중지: kill $BACKEND_PID $FRONTEND_PID"
echo "또는 Ctrl+C로 중지"
echo ""
echo "🌍 브라우저에서 http://localhost:3000 접속"

# 서버 실행 상태 유지
wait
