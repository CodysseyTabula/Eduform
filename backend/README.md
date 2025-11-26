# IEP Planning Support Service - Backend

## Overview
개별화 교육 계획(IEP) 자동 생성 및 관리 백엔드 서비스

## Tech Stack
- **Framework:** FastAPI 0.115.5
- **Database:** PostgreSQL 16
- **ORM:** SQLAlchemy 2.0.36
- **Python:** 3.11
- **Container:** Docker + docker-compose

## Setup

### Option 1: Docker (권장)

#### 1. 환경 변수 설정
```bash
cd backend
cp .env.example .env
# .env 파일 편집 (필요 시)
```

#### 2. 컨테이너 빌드 및 실행
```bash
# 프로젝트 루트에서 실행
docker compose up --build
```

#### 3. 검증
```bash
# 헬스 체크
curl http://localhost:8000/health

# DB 연결 확인
docker compose exec db pg_isready -U postgres

# 스토리지 마운트 확인
docker compose exec app ls /storage
```

#### 4. 중지
```bash
docker compose down

# 볼륨까지 제거 (데이터 삭제)
docker compose down -v
```

### Option 2: 로컬 개발

#### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your configuration
```

#### 3. Run PostgreSQL (Docker)
```bash
docker run -d \
  --name iep_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=iep_db \
  -p 5432:5432 \
  postgres:16
```

#### 4. Run Application
```bash
uvicorn app.main:app --reload
```

## API Documentation
- Swagger UI: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## Docker Commands

```bash
# 로그 확인
docker compose logs -f app

# 컨테이너 내부 접속
docker compose exec app bash

# DB 접속
docker compose exec db psql -U postgres -d iep_db

# 개별 서비스 재시작
docker compose restart app
```
