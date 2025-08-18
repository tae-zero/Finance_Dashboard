# 🚀 Finance Dashboard 개발 환경 가이드

## 📋 프로젝트 개요

**Finance Dashboard**는 Next.js 기반의 주식투자 대시보드로, React, Zustand, Axios, TypeScript, PWA 기술을 활용하여 구축되었습니다.

## 🛠️ 기술 스택

### Frontend
- **Next.js 14** - React 프레임워크
- **React 18** - UI 라이브러리
- **TypeScript** - 타입 안전성
- **Zustand** - 상태 관리
- **Axios** - HTTP 클라이언트
- **Tailwind CSS** - 스타일링
- **Chart.js** - 차트 라이브러리
- **PWA** - Progressive Web App

### Backend
- **FastAPI** - Python 웹 프레임워크
- **MongoDB** - 데이터베이스
- **Selenium** - 웹 스크래핑
- **yfinance** - 주식 데이터

## 🚀 빠른 시작

### 1. 저장소 클론
```bash
git clone https://github.com/tae-zero/Finance_Dashboard.git
cd Finance_Dashboard
```

### 2. 자동 개발 환경 설정
```bash
# Linux/Mac
chmod +x dev-setup.sh
./dev-setup.sh

# Windows
# PowerShell에서 실행
```

### 3. 수동 설정 (선택사항)

#### Frontend 설정
```bash
cd FRONTEND
npm install
npm run dev
```

#### Backend 설정
```bash
cd BACKEND
pip install -r requirements.txt
python main.py
```

## 🌍 환경별 설정

### 로컬 개발 환경
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:7000
- **API**: http://localhost:7000/api/v1

### 프로덕션 환경
- **Frontend**: Vercel
- **Backend**: Railway
- **API**: https://financedashboard-production-50f3.up.railway.app/api/v1

## 📁 프로젝트 구조

```
Finance_Dashboard/
├── FRONTEND/                 # Next.js 프론트엔드
│   ├── src/
│   │   ├── app/             # App Router
│   │   ├── components/      # React 컴포넌트
│   │   ├── stores/          # Zustand 스토어
│   │   └── config/          # 설정 파일
│   ├── public/              # 정적 파일 (PWA 아이콘 포함)
│   └── package.json
├── BACKEND/                  # FastAPI 백엔드
│   ├── routers/             # API 라우터
│   ├── services/            # 비즈니스 로직
│   ├── utils/               # 유틸리티
│   └── main.py
├── .github/                  # GitHub Actions
├── docker-compose.dev.yml    # 개발용 Docker
└── dev-setup.sh             # 개발 환경 설정 스크립트
```

## 🔧 개발 명령어

### Frontend
```bash
npm run dev          # 개발 서버 시작
npm run build        # 프로덕션 빌드
npm run start        # 프로덕션 서버 시작
npm run lint         # 코드 린팅
npm run test         # 테스트 실행
npm run type-check   # TypeScript 타입 체크
```

### Backend
```bash
python main.py       # 개발 서버 시작
uvicorn main:app --reload --port 7000  # 핫 리로드
```

## 🧪 테스트

### Frontend 테스트
```bash
cd FRONTEND
npm test             # Jest 테스트 실행
npm run test:watch   # 테스트 감시 모드
```

### Backend 테스트
```bash
cd BACKEND
python -m pytest     # pytest 실행
```

## 🚀 CI/CD 파이프라인

### GitHub Actions 워크플로우
- **Push to main**: 자동 배포
- **Pull Request**: 테스트 및 빌드 검증
- **Frontend**: Vercel 자동 배포
- **Backend**: Railway 자동 배포

### 환경변수 설정
GitHub Secrets에 다음 값들을 설정해야 합니다:

#### Vercel 배포
- `VERCEL_TOKEN`: Vercel API 토큰
- `ORG_ID`: Vercel 조직 ID
- `PROJECT_ID`: Vercel 프로젝트 ID

#### Railway 배포
- `RAILWAY_TOKEN`: Railway API 토큰
- `RAILWAY_SERVICE`: Railway 서비스 이름

## 📱 PWA 설정

### 매니페스트 파일
- `public/manifest.json`: PWA 설정
- `public/icon-192x192.png`: 192x192 아이콘
- `public/icon-512x512.png`: 512x512 아이콘

### 서비스 워커
- `next-pwa` 플러그인으로 자동 생성
- 개발 환경에서는 비활성화

## 🔒 환경변수 관리

### Frontend (.env.local)
```env
NODE_ENV=development
NEXT_PUBLIC_API_BASE_URL=http://localhost:7000/api/v1
NEXT_PUBLIC_ENVIRONMENT=local
```

### Backend (.env)
```env
MONGODB_URI=mongodb+srv://...
DB_NAME=testDB
HOST=0.0.0.0
PORT=7000
DEBUG=False
```

## 🐳 Docker 개발 환경

### 개발용 Docker 실행
```bash
docker-compose -f docker-compose.dev.yml up
```

### 서비스 접속
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:7000
- **MongoDB**: localhost:27017
- **Redis**: localhost:6379

## 🚨 문제 해결

### CORS 오류
1. Railway 환경변수 `CORS_ORIGINS` 확인
2. 새로운 Vercel 도메인 추가
3. 백엔드 재배포

### API 연결 실패
1. 환경변수 `NEXT_PUBLIC_API_BASE_URL` 확인
2. 백엔드 서버 상태 확인
3. 네트워크 연결 확인

### PWA 설치 실패
1. HTTPS 환경 확인 (프로덕션)
2. 매니페스트 파일 유효성 검사
3. 서비스 워커 등록 확인

## 📚 추가 리소스

- [Next.js 공식 문서](https://nextjs.org/docs)
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Zustand 공식 문서](https://github.com/pmndrs/zustand)
- [PWA 가이드](https://web.dev/progressive-web-apps/)

## 🤝 기여하기

1. Fork 저장소
2. 기능 브랜치 생성 (`git checkout -b feature/AmazingFeature`)
3. 변경사항 커밋 (`git commit -m 'Add some AmazingFeature'`)
4. 브랜치 푸시 (`git push origin feature/AmazingFeature`)
5. Pull Request 생성

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.
