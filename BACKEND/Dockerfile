# Python 3.11 slim 이미지 사용
FROM python:3.11-slim

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    gcc \
    g++ \
    make \
    git \
    && rm -rf /var/lib/apt/lists/*

# Chrome 설치
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# Poetry 설치 (의존성 관리를 위해)
RUN pip install poetry

# 프로젝트 파일 복사
COPY pyproject.toml poetry.lock* ./

# Poetry 설정 및 의존성 설치
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

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