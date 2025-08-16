# Next.js + Tailwind CSS 프로젝트 배포 가이드

## 🎯 프로젝트 변환 완료

기존 Vite + React 프로젝트를 **Next.js + React + Tailwind CSS**로 성공적으로 변환했습니다!

## 🚀 새로운 기술 스택

### 프론트엔드
- ✅ **Next.js 14** - React 프레임워크
- ✅ **React 18** - UI 라이브러리
- ✅ **Tailwind CSS 3** - 유틸리티 우선 CSS 프레임워크
- ✅ **TypeScript** - 타입 안전성

### 백엔드
- ✅ **FastAPI** - Python 웹 프레임워크 (변경 없음)

## 📦 설치 및 실행

### 1. 의존성 설치
```bash
cd FRONTEND
npm install
```

### 2. 개발 서버 실행
```bash
npm run dev
```

### 3. 프로덕션 빌드
```bash
npm run build
npm start
```

## 🌐 환경변수 설정

### 로컬 개발 (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 프로덕션 (Vercel)
```env
NEXT_PUBLIC_API_URL=https://your-railway-app-name.railway.app
```

## 🚀 배포 방법

### 1. Vercel에 배포 (프론트엔드)

1. **Vercel 계정 생성 및 로그인**
   - [vercel.com](https://vercel.com)에서 계정 생성
   - GitHub 계정으로 로그인

2. **프로젝트 배포**
   - "New Project" 클릭
   - GitHub 저장소 연결
   - **Framework Preset: Next.js** 자동 감지
   - 환경변수 설정: `NEXT_PUBLIC_API_URL`

3. **도메인 설정**
   - Vercel 대시보드 → Settings → Domains
   - 가비아에서 구매한 도메인 추가

### 2. Railway에 배포 (백엔드)

1. **Railway 계정 생성 및 로그인**
   - [railway.app](https://railway.app)에서 계정 생성
   - GitHub 계정으로 로그인

2. **프로젝트 배포**
   - "New Project" 클릭
   - "Deploy from GitHub repo" 선택
   - GitHub 저장소 연결

3. **환경변수 설정**
   ```env
   MONGODB_URI=your_mongodb_connection_string
   DB_NAME=investment_analysis
   FRONTEND_URL=https://your-vercel-app.vercel.app
   DEBUG=False
   ```

## 🔧 주요 변경사항

### 파일 구조
```
FRONTEND/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── layout.tsx         # 루트 레이아웃
│   │   ├── page.tsx           # 메인 페이지
│   │   └── globals.css        # Tailwind CSS
│   ├── components/             # React 컴포넌트
│   └── config/                 # 설정 파일
├── tailwind.config.js          # Tailwind 설정
├── next.config.js              # Next.js 설정
├── tsconfig.json               # TypeScript 설정
└── package.json                # Next.js 의존성
```

### 스타일링
- **기존 CSS** → **Tailwind CSS 클래스**
- **커스텀 CSS** → **@apply 디렉티브**
- **반응형 디자인** → **Tailwind 브레이크포인트**

### 라우팅
- **React Router** → **Next.js App Router**
- **클라이언트 라우팅** → **서버 컴포넌트 + 클라이언트 컴포넌트**

## 🎨 Tailwind CSS 활용

### 컴포넌트 클래스
```tsx
// 카드 컴포넌트
<div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
  <h2 className="text-2xl font-bold text-gray-900 mb-4">제목</h2>
  <p className="text-gray-700 leading-relaxed">내용</p>
</div>

// 버튼 컴포넌트
<button className="btn-primary">
  클릭하세요
</button>
```

### 커스텀 컴포넌트
```css
@layer components {
  .btn-primary {
    @apply bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200;
  }
  
  .card {
    @apply bg-white rounded-lg shadow-sm border border-gray-200 p-6;
  }
}
```

## 📱 반응형 디자인

### Tailwind 브레이크포인트
- **sm**: 640px 이상
- **md**: 768px 이상
- **lg**: 1024px 이상
- **xl**: 1280px 이상

### 예시
```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {/* 모바일: 1열, 태블릿: 2열, 데스크톱: 3열 */}
</div>
```

## 🔍 문제 해결

### 1. 빌드 오류
```bash
# TypeScript 오류 확인
npm run lint

# 타입 체크
npx tsc --noEmit
```

### 2. Tailwind CSS가 작동하지 않음
```bash
# PostCSS 캐시 삭제
rm -rf .next
npm run dev
```

### 3. API 연결 오류
- 환경변수 `NEXT_PUBLIC_API_URL` 확인
- CORS 설정 확인
- 백엔드 서버 상태 확인

## 📚 참고 자료

- [Next.js 공식 문서](https://nextjs.org/docs)
- [Tailwind CSS 공식 문서](https://tailwindcss.com/docs)
- [Vercel Next.js 배포 가이드](https://vercel.com/docs/functions/deploying-from-cli#deploying-nextjs-projects)
- [Railway Python 배포 가이드](https://docs.railway.app/deploy/deployments)

## 🎉 변환 완료!

이제 **Next.js + React + Tailwind CSS** 기반의 현대적인 웹 애플리케이션으로 배포할 수 있습니다!

### 다음 단계
1. `npm install`로 의존성 설치
2. `npm run dev`로 로컬 테스트
3. Vercel과 Railway에 배포
4. 가비아 도메인 연결
