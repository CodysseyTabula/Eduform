FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# Python 환경 변수
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 시스템 의존성 설치 (PostgreSQL 클라이언트 라이브러리 및 빌드 도구)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libpq-dev \
    libc6-dev \
    && rm -rf /var/lib/apt/lists/*

# pip 업그레이드
RUN pip install --upgrade pip

# 의존성 파일 복사 및 설치 (레이어 캐싱 최적화)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY app ./app
COPY tests ./tests

# 스토리지 디렉토리 생성
RUN mkdir -p /storage

# 포트 노출
EXPOSE 8000

# 개발 모드 실행 명령 (--reload)
# 프로덕션에서는 --reload 제거 권장
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
