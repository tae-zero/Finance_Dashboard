FROM python:3.11-slim

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Chrome 설치 (ChromeDriver 114와 호환되는 버전)
RUN curl -fsSL https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -o /tmp/chrome.deb \
    && apt-get update \
    && apt-get install -y /tmp/chrome.deb \
    && rm /tmp/chrome.deb \
    && rm -rf /var/lib/apt/lists/*

# ChromeDriver 설치 (고정 버전 114.0.5735.90)
RUN wget -q https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip -O /tmp/chromedriver.zip \
    && unzip /tmp/chromedriver.zip -d /usr/local/bin/ \
    && rm /tmp/chromedriver.zip \
    && chmod +x /usr/local/bin/chromedriver

# Chrome 버전 확인 및 제한
RUN google-chrome --version && chromedriver --version

# 작업 디렉토리 설정
WORKDIR /app

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 포트 노출
EXPOSE 7000

# 애플리케이션 실행
CMD ["python", "start.py"]