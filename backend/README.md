# IEP Planning Support Service - Backend

## Overview
개별화 교육 계획(IEP) 자동 생성 및 관리 백엔드 서비스

## Tech Stack
- **Framework:** FastAPI 0.115.5
- **Database:** PostgreSQL 17
- **ORM:** SQLAlchemy 2.0.36
- **Python:** 3.14

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Run Application
```bash
uvicorn app.main:app --reload
```

## API Documentation
- Swagger UI: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

