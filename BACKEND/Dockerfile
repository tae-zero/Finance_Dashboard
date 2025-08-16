# Python 3.11 slim 이미지 사용
FROM python:3.11-slim

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    wget \
    gnupg2 \
    unzip \
    gcc \
    g++ \
    make \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Chrome 설치
RUN mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /etc/apt/keyrings/google-chrome.gpg && \
    echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# Chrome 환경변수 설정
ENV CHROME_BIN=/usr/bin/google-chrome
ENV CHROME_PATH=/usr/bin/google-chrome
ENV CHROMIUM_PATH=/usr/bin/google-chrome

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

# 환경 변수 설정
ENV PORT=7000
ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Seoul

# 한국 시간대 설정
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 실행 권한 설정
RUN chmod +x /app/start.sh

# 시작 스크립트 실행
CMD ["/app/start.sh"]