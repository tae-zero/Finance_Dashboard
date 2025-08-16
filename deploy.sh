#!/bin/bash

echo "🚀 프로젝트 배포 시작..."

# 1. 프론트엔드 빌드
echo "📦 프론트엔드 빌드 중..."
cd FRONTEND
npm install
npm run build
echo "✅ 프론트엔드 빌드 완료"

# 2. 백엔드 의존성 확인
echo "🐍 백엔드 의존성 확인 중..."
cd ../BACKEND
pip install -r requirements.txt
echo "✅ 백엔드 의존성 설치 완료"

# 3. 환경변수 파일 생성 안내
echo ""
echo "📝 다음 단계를 진행해주세요:"
echo ""
echo "1. Vercel에 프론트엔드 배포:"
echo "   - https://vercel.com 에서 새 프로젝트 생성"
echo "   - GitHub 저장소 연결"
echo "   - 환경변수 VITE_API_URL 설정"
echo ""
echo "2. Railway에 백엔드 배포:"
echo "   - https://railway.app 에서 새 프로젝트 생성"
echo "   - GitHub 저장소 연결"
echo "   - 환경변수 설정 (env.example 참고)"
echo ""
echo "3. 가비아 DNS 설정:"
echo "   - CNAME 레코드로 Vercel과 Railway 연결"
echo ""
echo "자세한 내용은 DEPLOYMENT_GUIDE.md 파일을 참고하세요."
echo ""
echo "🎉 배포 준비 완료!"
