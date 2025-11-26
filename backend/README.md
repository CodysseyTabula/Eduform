# IEP Planning Support Service - Backend

## 📋 개요 (Overview)

개별화 교육 계획(IEP, Individualized Education Program) 자동 생성 및 관리를 위한 백엔드 서비스입니다. FastAPI 기반으로 구축되었으며, AI 모듈을 통해 학생 프로필을 기반으로 연간/학기 목표, 주차별 학습 계획, 학습 자료를 자동 생성합니다.

## 🛠️ 기술 스택 (Tech Stack)

- **Framework:** FastAPI 0.115.5
- **Database:** PostgreSQL 16
- **ORM:** SQLAlchemy 2.0.36
- **Python:** 3.11+
- **Container:** Docker + docker-compose
- **Document Generation:** python-docx 1.1.2
- **Testing:** pytest 8.3.4

## 📚 주요 기능

1. **학생 관리**: 학생 기본 정보 생성 및 조회
2. **IEP 버전 관리**: 학기별 IEP 버전 생성 및 조회
3. **IEP 파일 생성**: AI 모듈 기반 3개 JSON 파일 자동 생성
   - `goals.json`: 연간/학기 목표 (도메인별)
   - `weekly_plan.json`: 주차별 학습 내용 (20주)
   - `weekly_materials.json`: 주차별 학습 자료 (URL 참조)
4. **DOCX 다운로드**: IEP 문서를 Word 파일로 생성 및 다운로드

## 🚀 빠른 시작 (Quick Start)

### 필수 요구사항

- Docker Desktop (권장) 또는
- Python 3.11+ & PostgreSQL 16

---

## 📦 Option 1: Docker 사용 (권장)

### 1. 환경 변수 설정

프로젝트 루트에 `.env` 파일을 생성하거나 기본값을 사용합니다:

```bash
# 데이터베이스 설정
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=iep_db
DB_PORT=5432

# 애플리케이션 설정
APP_PORT=8000
APP_DEBUG=true
APP_ENV=docker
```

### 2. 컨테이너 빌드 및 실행

```bash
# 프로젝트 루트에서 실행
docker compose up --build

# 또는 백그라운드 실행
docker compose up -d --build
```

### 3. 서비스 확인

```bash
# 헬스 체크
curl http://localhost:8000/health

# API 문서 확인 (브라우저)
open http://localhost:8000/docs

# DB 연결 확인
docker compose exec db pg_isready -U postgres

# 스토리지 마운트 확인
docker compose exec app ls -la /storage
```

### 4. 로그 확인

```bash
# 전체 로그
docker compose logs -f

# 백엔드만
docker compose logs -f app

# DB만
docker compose logs -f db
```

### 5. 중지 및 정리

```bash
# 중지
docker compose down

# 볼륨까지 제거 (데이터 삭제)
docker compose down -v

# 이미지까지 제거
docker compose down --rmi all -v
```

---

## 💻 Option 2: 로컬 개발 환경

### 1. Python 의존성 설치

```bash
cd backend

# 가상환경 생성 (권장)
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. PostgreSQL 실행

**Docker로 PostgreSQL만 실행:**

```bash
docker run -d \
  --name iep_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=iep_db \
  -p 5432:5432 \
  postgres:16
```

**또는 로컬 PostgreSQL 사용:**
- PostgreSQL 16 설치 후 `iep_db` 데이터베이스 생성

### 3. 환경 변수 설정

`backend/.env` 파일 생성:

```bash
# 데이터베이스
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=iep_db

# 스토리지
STORAGE_PATH=./storage

# 애플리케이션
APP_DEBUG=true
```

### 4. 데이터베이스 초기화

애플리케이션 시작 시 자동으로 테이블이 생성됩니다 (`Base.metadata.create_all`).

### 5. 애플리케이션 실행

```bash
# backend 폴더에서 실행
uvicorn app.main:app --reload

# 또는 포트 지정
uvicorn app.main:app --reload --port 8000 --host 0.0.0.0
```

### 6. 확인

```bash
# 헬스 체크
curl http://localhost:8000/health

# API 문서
open http://localhost:8000/docs
```

---

## 🧪 테스트 실행

### 전체 테스트

```bash
cd backend

# pytest 실행
pytest

# 커버리지 포함
pytest --cov=app --cov-report=html

# 상세 출력
pytest -v

# 특정 테스트만
pytest tests/test_students.py
pytest tests/test_iep_integration.py -v
```

### Docker 환경에서 테스트

```bash
# 컨테이너 내부 접속
docker compose exec app bash

# pytest 실행
pytest

# 종료
exit
```

---

## 📂 스토리지 구조

### 파일 경로 패턴

```
{STORAGE_PATH}/
└── iep/
    └── {iep_version_id}/
        ├── goals-{timestamp}.json
        ├── weekly_plan-{timestamp}.json
        └── weekly_materials-{timestamp}.json
```

### 예시

```
./storage/
└── iep/
    └── 550e8400-e29b-41d4-a716-446655440000/
        ├── goals-1735210800.json
        ├── weekly_plan-1735210801.json
        └── weekly_materials-1735210802.json
```

### 접근 권한 설정

**Docker 환경:**
- 자동으로 `/storage` 볼륨이 마운트됩니다
- `backend/storage` 폴더가 컨테이너 내 `/storage`에 바인딩됩니다

**로컬 환경:**

```bash
# storage 폴더 생성
mkdir -p backend/storage/iep

# 권한 확인
ls -la backend/storage
```

---

## 🔧 개발 도구

### Docker 명령어 모음

```bash
# 컨테이너 내부 접속
docker compose exec app bash

# DB 직접 접속
docker compose exec db psql -U postgres -d iep_db

# 특정 서비스만 재시작
docker compose restart app

# 전체 재빌드
docker compose up --build --force-recreate

# 볼륨 확인
docker volume ls
docker volume inspect eduform_postgres_data
```

### 데이터베이스 작업

```bash
# PostgreSQL 접속 (Docker)
docker compose exec db psql -U postgres -d iep_db

# 테이블 확인
\dt

# 학생 목록 조회
SELECT * FROM students;

# IEP 버전 목록
SELECT * FROM iep_versions;

# IEP 파일 목록
SELECT * FROM iep_files;

# 종료
\q
```

### 로그 및 디버깅

```bash
# 실시간 로그
docker compose logs -f app

# 최근 100줄
docker compose logs --tail=100 app

# 특정 시간 이후
docker compose logs --since 2024-01-01T00:00:00 app
```

---

## 📖 API 문서

### 자동 생성 문서

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 주요 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/health` | 헬스 체크 |
| POST | `/students` | 학생 생성 |
| GET | `/students` | 학생 목록 조회 |
| POST | `/iep-versions` | IEP 버전 생성 |
| GET | `/students/{id}/iep-latest` | 최신 IEP 조회 |
| GET | `/students/{id}/iep-versions` | IEP 목록 조회 |
| POST | `/iep-files` | IEP 파일 생성 (AI) |
| GET | `/iep-versions/{id}/iep-files` | IEP 파일 목록 |
| GET | `/iep-files/{id}/content` | IEP 파일 내용 조회 |
| PUT | `/iep-files/{id}` | IEP 파일 업데이트 |
| GET | `/iep-versions/{id}/docx` | DOCX 다운로드 |

상세 사용법은 [`docs/API.md`](docs/API.md)를 참조하세요.

---

## 🏗️ 프로젝트 구조

```
backend/
├── app/
│   ├── api/              # API 라우터
│   │   ├── students.py
│   │   ├── iep_versions.py
│   │   └── iep_files.py
│   ├── core/             # 설정
│   │   └── config.py
│   ├── db/               # 데이터베이스
│   │   ├── base.py
│   │   └── session.py
│   ├── models/           # ORM 모델
│   │   ├── student.py
│   │   ├── iep_version.py
│   │   └── iep_file.py
│   ├── schemas/          # Pydantic 스키마
│   │   ├── student.py
│   │   ├── iep_version.py
│   │   ├── iep_file.py
│   │   └── student_profile.py
│   ├── services/         # 비즈니스 로직
│   │   ├── ai_integration.py
│   │   ├── file_storage.py
│   │   ├── document_generator.py
│   │   └── iep_business.py
│   └── main.py           # FastAPI 앱
├── ai_module/            # AI 모듈
│   └── generators.py
├── tests/                # 테스트
├── storage/              # 파일 저장소
├── docs/                 # 추가 문서
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## ⚙️ 환경 변수 전체 목록

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `DB_HOST` | `localhost` | PostgreSQL 호스트 |
| `DB_PORT` | `5432` | PostgreSQL 포트 |
| `DB_USER` | `postgres` | DB 사용자 |
| `DB_PASSWORD` | `postgres` | DB 비밀번호 |
| `DB_NAME` | `iep_db` | 데이터베이스 이름 |
| `STORAGE_PATH` | `./storage` | 파일 저장 경로 |
| `APP_DEBUG` | `true` | 디버그 모드 |
| `APP_PORT` | `8000` | 애플리케이션 포트 |

---

## 🔒 STOP & ASK 개발 규칙

### 커밋 메시지 형식

```
<emoji> <type> : <description> (<file>) #<issue>
```

**예시:**
```
🎨 feat : IEP 파일 생성 API 구현 (app/api/iep_files.py) #n9
🐛 fix : DOCX 생성 시 인코딩 오류 수정 (services/document_generator.py) #n12
📝 docs : API 문서 추가 (docs/API.md) #44
🧪 test : IEP 통합 테스트 추가 (tests/test_iep_integration.py) #n13
```

### 브랜치 전략

```
<category>/<feature-name>/<developer-id>
```

**예시:**
```
feat/student-feature/sh
feat/iep-file-create-api/sh
docs/documentation/sh
fix/docx-encoding/sh
```

### PR 규칙

1. **절대 직접 커밋 금지** - 반드시 사용자 승인 후 커밋
2. **작은 단위로 작업** - 하나의 이슈는 여러 개의 작은 커밋으로 구성
3. **테스트 필수** - 모든 코드 변경은 테스트 포함
4. **문서 업데이트** - API 변경 시 문서도 함께 업데이트

---

## 📚 추가 문서

- **[API 문서](docs/API.md)**: 전체 엔드포인트 상세 가이드
- **[아키텍처 문서](docs/architecture.md)**: 시스템 설계 및 데이터 흐름
- **[개발자 가이드](docs/dev_guide.md)**: 개발 규칙 및 베스트 프랙티스
- **[LLM 프롬프트 사양](references/llm_prompt_specification.md)**: AI 모듈 인터페이스
- **[로드맵](instructions/roadmap.md)**: 프로젝트 이슈 및 진행 상황

---

## 🐛 트러블슈팅

### Docker 관련

**문제: 포트 충돌**
```bash
# 사용 중인 포트 확인
lsof -i :8000
lsof -i :5432

# .env 파일에서 포트 변경
APP_PORT=8001
DB_PORT=5433
```

**문제: 볼륨 권한 오류**
```bash
# 볼륨 삭제 후 재생성
docker compose down -v
docker compose up --build
```

**문제: 이미지 빌드 실패**
```bash
# 캐시 없이 재빌드
docker compose build --no-cache
docker compose up
```

### 데이터베이스 관련

**문제: 연결 실패**
```bash
# DB 컨테이너 상태 확인
docker compose ps db

# 로그 확인
docker compose logs db

# 연결 테스트
docker compose exec db pg_isready -U postgres
```

**문제: 테이블이 생성되지 않음**
```bash
# 컨테이너 재시작 (자동으로 create_all 실행)
docker compose restart app

# 또는 수동으로 Python 실행
docker compose exec app python -c "from app.db.base import Base; from app.db.session import engine; import app.models; Base.metadata.create_all(bind=engine)"
```

### 테스트 관련

**문제: 테스트 실패**
```bash
# 상세 로그로 재실행
pytest -vv -s

# 특정 테스트만
pytest tests/test_students.py::test_create_student -vv

# 캐시 삭제
pytest --cache-clear
```

---

## 📞 문의 및 기여

- **이슈**: GitHub Issues
- **문서**: `backend/docs/` 폴더
- **로드맵**: `backend/instructions/roadmap.md`

---

**최종 업데이트**: 2024-12-26  
**버전**: 1.0.0  
**작성자**: Backend Team
