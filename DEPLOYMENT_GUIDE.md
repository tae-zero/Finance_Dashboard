# 프로젝트 배포 가이드

## 1. 프론트엔드 배포 (Vercel)

### 1.1 Vercel 계정 생성 및 로그인
1. [Vercel](https://vercel.com)에 접속하여 계정 생성
2. GitHub 계정으로 로그인

### 1.2 프로젝트 배포
1. Vercel 대시보드에서 "New Project" 클릭
2. GitHub 저장소 연결
3. 프로젝트 설정:
   - Framework Preset: Vite
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm install`

### 1.3 환경변수 설정
Vercel 대시보드 → Settings → Environment Variables에서:
```
VITE_API_URL=https://your-railway-app-name.railway.app
```

### 1.4 도메인 설정
1. Vercel 대시보드 → Settings → Domains
2. "Add Domain" 클릭
3. 가비아에서 구매한 도메인 입력
4. DNS 설정 안내에 따라 가비아 DNS 관리에서 설정

## 2. 백엔드 배포 (Railway)

### 2.1 Railway 계정 생성 및 로그인
1. [Railway](https://railway.app)에 접속하여 계정 생성
2. GitHub 계정으로 로그인

### 2.2 프로젝트 배포
1. Railway 대시보드에서 "New Project" 클릭
2. "Deploy from GitHub repo" 선택
3. GitHub 저장소 연결
4. 프로젝트 설정:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 2.3 환경변수 설정
Railway 대시보드 → Variables에서:
```
MONGODB_URI=your_mongodb_connection_string
DB_NAME=investment_analysis
COLLECTION_USERS=users
COLLECTION_EXPLAIN=explain
COLLECTION_OUTLINE=outline
COLLECTION_INDUSTRY=industry
HOST=0.0.0.0
PORT=8000
FRONTEND_URL=https://your-vercel-app.vercel.app
DEBUG=False
```

### 2.4 MongoDB 설정
1. Railway에서 MongoDB 서비스 추가
2. MongoDB 연결 문자열을 환경변수에 설정

## 3. 도메인 연결 (가비아)

### 3.1 DNS 설정
가비아 DNS 관리에서 다음 레코드 추가:

#### 프론트엔드 (Vercel)
```
Type: CNAME
Name: @ 또는 www
Value: cname.vercel-dns.com
TTL: 3600
```

#### 백엔드 (Railway)
```
Type: CNAME
Name: api
Value: your-railway-app-name.railway.app
TTL: 3600
```

### 3.2 SSL 인증서
- Vercel과 Railway는 자동으로 SSL 인증서를 제공
- 가비아에서도 SSL 인증서 구매 가능

## 4. 배포 후 확인사항

### 4.1 프론트엔드 확인
- Vercel 배포 URL로 접속
- API 호출이 정상적으로 작동하는지 확인
- 콘솔 에러 확인

### 4.2 백엔드 확인
- Railway 배포 URL로 접속
- `/health` 엔드포인트로 서버 상태 확인
- API 문서 (`/docs`) 접근 확인

### 4.3 도메인 연결 확인
- 구매한 도메인으로 접속
- SSL 인증서 정상 작동 확인
- API 호출 정상 작동 확인

## 5. 문제 해결

### 5.1 CORS 오류
- 백엔드 CORS 설정에서 프론트엔드 도메인 추가
- 환경변수 `FRONTEND_URL` 확인

### 5.2 API 연결 오류
- 환경변수 `VITE_API_URL` 확인
- 백엔드 서버 상태 확인
- 네트워크 요청 로그 확인

### 5.3 빌드 오류
- 의존성 버전 호환성 확인
- Node.js 및 Python 버전 확인
- 빌드 로그 상세 분석

## 6. 유지보수

### 6.1 자동 배포
- GitHub에 코드 푸시 시 자동 배포
- Vercel과 Railway 모두 자동 배포 지원

### 6.2 모니터링
- Vercel Analytics 활용
- Railway 로그 모니터링
- 에러 추적 및 알림 설정

### 6.3 백업
- MongoDB 데이터 정기 백업
- 코드 저장소 백업
- 환경변수 백업
