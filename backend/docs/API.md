# API Documentation

## 📋 개요

IEP Planning Support 백엔드 API의 전체 엔드포인트 및 사용법을 설명합니다.

**Base URL**: `http://localhost:8000` (로컬 개발)

**API 문서 (자동 생성)**:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 📑 목차

1. [인증 (Authentication)](#인증-authentication)
2. [학생 관리 (Students)](#학생-관리-students)
3. [IEP 버전 관리 (IEP Versions)](#iep-버전-관리-iep-versions)
4. [IEP 파일 관리 (IEP Files)](#iep-파일-관리-iep-files)
5. [DOCX 생성 (Document Generation)](#docx-생성-document-generation)
6. [스키마 참조 (Schema Reference)](#스키마-참조-schema-reference)
7. [오류 처리 (Error Handling)](#오류-처리-error-handling)

---

## 인증 (Authentication)

**현재 버전**: 인증 없음 (개발 단계)

**향후 계획**: JWT 토큰 기반 인증 추가 예정

---

## 학생 관리 (Students)

### 1. 학생 생성

학생 기본 정보를 생성합니다.

**Endpoint**: `POST /students`

**Request Body**:
```json
{
  "name": "홍길동",
  "birth": "2010-03-15"
}
```

**Response** (201 Created):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "홍길동",
  "birth": "2010-03-15"
}
```

**cURL 예시**:
```bash
curl -X POST "http://localhost:8000/students" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "홍길동",
    "birth": "2010-03-15"
  }'
```

**Python 예시**:
```python
import httpx

response = httpx.post(
    "http://localhost:8000/students",
    json={
        "name": "홍길동",
        "birth": "2010-03-15"
    }
)
student = response.json()
print(f"학생 ID: {student['id']}")
```

---

### 2. 학생 목록 조회

전체 학생 목록을 조회합니다.

**Endpoint**: `GET /students`

**Response** (200 OK):
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "홍길동",
    "birth": "2010-03-15"
  },
  {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "name": "김영희",
    "birth": "2011-07-22"
  }
]
```

**cURL 예시**:
```bash
curl -X GET "http://localhost:8000/students"
```

**Python 예시**:
```python
import httpx

response = httpx.get("http://localhost:8000/students")
students = response.json()

for student in students:
    print(f"{student['name']} ({student['birth']})")
```

---

## IEP 버전 관리 (IEP Versions)

### 3. IEP 버전 생성

학기별 IEP 버전을 생성합니다.

**Endpoint**: `POST /iep-versions`

**Request Body**:
```json
{
  "student_id": "550e8400-e29b-41d4-a716-446655440000",
  "year": "2024",
  "semester": "1학기",
  "grade": "5"
}
```

**Response** (201 Created):
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "student_id": "550e8400-e29b-41d4-a716-446655440000",
  "year": "2024",
  "semester": "1학기",
  "grade": "5",
  "created_at": "2024-12-26T10:30:00.000Z"
}
```

**cURL 예시**:
```bash
curl -X POST "http://localhost:8000/iep-versions" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "550e8400-e29b-41d4-a716-446655440000",
    "year": "2024",
    "semester": "1학기",
    "grade": "5"
  }'
```

---

### 4. 학생 최신 IEP 조회

해당 학생의 가장 최근 IEP 버전을 조회합니다.

**Endpoint**: `GET /students/{student_id}/iep-latest`

**Response** (200 OK):
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "student_id": "550e8400-e29b-41d4-a716-446655440000",
  "year": "2024",
  "semester": "2학기",
  "grade": "5",
  "created_at": "2024-08-15T10:30:00.000Z"
}
```

**Response** (404 Not Found) - IEP가 없는 경우:
```json
{
  "detail": "No IEP version found for this student"
}
```

**cURL 예시**:
```bash
curl -X GET "http://localhost:8000/students/550e8400-e29b-41d4-a716-446655440000/iep-latest"
```

---

### 5. 학생 IEP 목록 조회

학생의 전체 IEP 버전 목록을 조회합니다 (사이드바 표시용).

**Endpoint**: `GET /students/{student_id}/iep-versions`

**Response** (200 OK):
```json
[
  {
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "year": "2024",
    "semester": "2학기",
    "grade": "5",
    "created_at": "2024-08-15T10:30:00.000Z"
  },
  {
    "id": "880e8400-e29b-41d4-a716-446655440003",
    "year": "2024",
    "semester": "1학기",
    "grade": "5",
    "created_at": "2024-03-10T10:30:00.000Z"
  }
]
```

**cURL 예시**:
```bash
curl -X GET "http://localhost:8000/students/550e8400-e29b-41d4-a716-446655440000/iep-versions"
```

---

## IEP 파일 관리 (IEP Files)

### 6. IEP 파일 생성 (AI 기반)

학생 프로필을 기반으로 AI 모듈을 통해 3개의 IEP JSON 파일을 자동 생성합니다.

**Endpoint**: `POST /iep-files`

**Request Body**:
```json
{
  "iep_version_id": "770e8400-e29b-41d4-a716-446655440002",
  "student_profile": {
    "name": "홍길동",
    "birth": "2010-03-15",
    "grade": 5,
    "current_semester": 1,
    "start_date": "2024-03-01",
    "end_date": "2024-07-20",
    "guardian_opinion": "학습 의욕이 높으나 집중력이 부족함",
    "cognitive_level": "평균 수준",
    "social_psych_level": "또래 관계 양호",
    "motor_daily_level": "정상 발달",
    "vci_score": 95,
    "visual_spatial_score": 92,
    "fri_score": 88,
    "wmi_score": 90,
    "psi_score": 85,
    "fsiq_score": 90,
    "korean_performance_level": "학년 수준의 80% 달성",
    "math_performance_level": "학년 수준의 75% 달성",
    "korean_domain": ["읽기", "쓰기"],
    "math_domain": ["수와 연산", "도형과 측정"]
  }
}
```

**Response** (201 Created):
```json
{
  "message": "IEP files created successfully",
  "files": [
    {
      "id": "aa0e8400-e29b-41d4-a716-446655440004",
      "iep_version_id": "770e8400-e29b-41d4-a716-446655440002",
      "file_type": "goals",
      "file_path": "/storage/iep/770e8400-e29b-41d4-a716-446655440002/goals-1735210800.json",
      "updated_at": "2024-12-26T10:30:00.000Z"
    },
    {
      "id": "bb0e8400-e29b-41d4-a716-446655440005",
      "iep_version_id": "770e8400-e29b-41d4-a716-446655440002",
      "file_type": "weekly_plan",
      "file_path": "/storage/iep/770e8400-e29b-41d4-a716-446655440002/weekly_plan-1735210801.json",
      "updated_at": "2024-12-26T10:30:01.000Z"
    },
    {
      "id": "cc0e8400-e29b-41d4-a716-446655440006",
      "iep_version_id": "770e8400-e29b-41d4-a716-446655440002",
      "file_type": "weekly_materials",
      "file_path": "/storage/iep/770e8400-e29b-41d4-a716-446655440002/weekly_materials-1735210802.json",
      "updated_at": "2024-12-26T10:30:02.000Z"
    }
  ]
}
```

**cURL 예시**:
```bash
curl -X POST "http://localhost:8000/iep-files" \
  -H "Content-Type: application/json" \
  -d @student_profile.json
```

**Python 예시**:
```python
import httpx

student_profile = {
    "iep_version_id": "770e8400-e29b-41d4-a716-446655440002",
    "student_profile": {
        "name": "홍길동",
        "birth": "2010-03-15",
        "grade": 5,
        "current_semester": 1,
        "start_date": "2024-03-01",
        "end_date": "2024-07-20",
        "guardian_opinion": "학습 의욕이 높으나 집중력이 부족함",
        "cognitive_level": "평균 수준",
        "social_psych_level": "또래 관계 양호",
        "motor_daily_level": "정상 발달",
        "vci_score": 95,
        "visual_spatial_score": 92,
        "fri_score": 88,
        "wmi_score": 90,
        "psi_score": 85,
        "fsiq_score": 90,
        "korean_performance_level": "학년 수준의 80% 달성",
        "math_performance_level": "학년 수준의 75% 달성",
        "korean_domain": ["읽기", "쓰기"],
        "math_domain": ["수와 연산", "도형과 측정"]
    }
}

response = httpx.post(
    "http://localhost:8000/iep-files",
    json=student_profile,
    timeout=60.0  # AI 처리 시간 고려
)

result = response.json()
print(f"생성된 파일 수: {len(result['files'])}")
```

---

### 7. IEP 파일 목록 조회

특정 IEP 버전의 모든 파일 메타데이터를 조회합니다.

**Endpoint**: `GET /iep-versions/{iep_version_id}/iep-files`

**Response** (200 OK):
```json
[
  {
    "id": "aa0e8400-e29b-41d4-a716-446655440004",
    "file_type": "goals",
    "file_path": "/storage/iep/770e8400-e29b-41d4-a716-446655440002/goals-1735210800.json",
    "updated_at": "2024-12-26T10:30:00.000Z"
  },
  {
    "id": "bb0e8400-e29b-41d4-a716-446655440005",
    "file_type": "weekly_plan",
    "file_path": "/storage/iep/770e8400-e29b-41d4-a716-446655440002/weekly_plan-1735210801.json",
    "updated_at": "2024-12-26T10:30:01.000Z"
  },
  {
    "id": "cc0e8400-e29b-41d4-a716-446655440006",
    "file_type": "weekly_materials",
    "file_path": "/storage/iep/770e8400-e29b-41d4-a716-446655440002/weekly_materials-1735210802.json",
    "updated_at": "2024-12-26T10:30:02.000Z"
  }
]
```

**cURL 예시**:
```bash
curl -X GET "http://localhost:8000/iep-versions/770e8400-e29b-41d4-a716-446655440002/iep-files"
```

---

### 8. IEP 파일 내용 조회

특정 IEP 파일의 JSON 내용을 조회합니다.

**Endpoint**: `GET /iep-files/{file_id}/content`

**Response** (200 OK) - `goals.json` 예시:
```json
{
  "annual_reading_goal": "5학년 수준의 문학 작품을 읽고 주제를 파악할 수 있다",
  "semester_reading_goal": "1학기 동안 단편 동화 10편을 읽고 줄거리를 요약할 수 있다",
  "annual_writing_goal": "자신의 생각과 느낌을 문장으로 표현할 수 있다",
  "semester_writing_goal": "1학기 동안 일기를 주 3회 이상 작성할 수 있다",
  "annual_numbersOperations_goal": "네 자리 수의 덧셈과 뺄셈을 할 수 있다",
  "semester_numbersOperations_goal": "1학기 동안 세 자리 수의 덧셈과 뺄셈을 완성한다",
  "annual_geometryMeasurement_goal": "기본 도형의 넓이를 구할 수 있다",
  "semester_geometryMeasurement_goal": "1학기 동안 직사각형과 정사각형의 넓이를 구한다"
}
```

**Response** (200 OK) - `weekly_plan.json` 예시:
```json
{
  "reading_weeklyContent": [
    "1주차: 동화책 '어린 왕자' 1-2장 읽기",
    "2주차: 동화책 '어린 왕자' 3-4장 읽고 줄거리 정리",
    "3주차: 단편 동화 '흥부와 놀부' 읽기",
    // ... 총 20개
  ],
  "writing_weeklyContent": [
    "1주차: 주말에 있었던 일 일기 쓰기",
    "2주차: 좋아하는 음식에 대해 쓰기",
    "3주차: 가족 소개 글쓰기",
    // ... 총 20개
  ],
  "numbersOperations_weeklyContent": [
    "1주차: 100 이내의 수 덧셈",
    "2주차: 100 이내의 수 뺄셈",
    "3주차: 세 자리 수 알아보기",
    // ... 총 20개
  ],
  "geometryMeasurement_weeklyContent": [
    "1주차: 도형의 종류 알아보기",
    "2주차: 직사각형의 특징",
    "3주차: 정사각형의 특징",
    // ... 총 20개
  ]
}
```

**cURL 예시**:
```bash
curl -X GET "http://localhost:8000/iep-files/aa0e8400-e29b-41d4-a716-446655440004/content"
```

---

### 9. IEP 파일 업데이트

기존 IEP 파일의 내용을 수정합니다 (덮어쓰기).

**Endpoint**: `PUT /iep-files/{file_id}`

**Request Body**:
```json
{
  "annual_reading_goal": "5학년 수준의 다양한 문학 작품을 읽고 주제를 파악할 수 있다",
  "semester_reading_goal": "1학기 동안 단편 동화 15편을 읽고 줄거리를 요약할 수 있다",
  "annual_writing_goal": "자신의 생각과 느낌을 문장으로 표현할 수 있다",
  "semester_writing_goal": "1학기 동안 일기를 매일 작성할 수 있다"
}
```

**Response** (200 OK):
```json
{
  "id": "aa0e8400-e29b-41d4-a716-446655440004",
  "iep_version_id": "770e8400-e29b-41d4-a716-446655440002",
  "file_type": "goals",
  "file_path": "/storage/iep/770e8400-e29b-41d4-a716-446655440002/goals-1735211000.json",
  "updated_at": "2024-12-26T10:35:00.000Z"
}
```

**cURL 예시**:
```bash
curl -X PUT "http://localhost:8000/iep-files/aa0e8400-e29b-41d4-a716-446655440004" \
  -H "Content-Type: application/json" \
  -d '{
    "annual_reading_goal": "수정된 연간 목표",
    "semester_reading_goal": "수정된 학기 목표"
  }'
```

---

## DOCX 생성 (Document Generation)

### 10. IEP DOCX 다운로드

IEP 버전의 모든 JSON 파일을 기반으로 Word 문서를 생성하고 다운로드합니다.

**Endpoint**: `GET /iep-versions/{iep_version_id}/docx`

**Response**: Binary stream (application/vnd.openxmlformats-officedocument.wordprocessingml.document)

**Headers**:
```
Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document
Content-Disposition: attachment; filename="IEP_{student_name}_{year}_{semester}.docx"
```

**cURL 예시**:
```bash
curl -X GET "http://localhost:8000/iep-versions/770e8400-e29b-41d4-a716-446655440002/docx" \
  -o "IEP_홍길동_2024_1학기.docx"
```

**Python 예시**:
```python
import httpx

iep_version_id = "770e8400-e29b-41d4-a716-446655440002"

response = httpx.get(
    f"http://localhost:8000/iep-versions/{iep_version_id}/docx",
    timeout=30.0
)

# 파일로 저장
with open("IEP_document.docx", "wb") as f:
    f.write(response.content)

print("DOCX 파일 다운로드 완료")
```

**JavaScript (fetch) 예시**:
```javascript
const iepVersionId = "770e8400-e29b-41d4-a716-446655440002";

fetch(`http://localhost:8000/iep-versions/${iepVersionId}/docx`)
  .then(response => response.blob())
  .then(blob => {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `IEP_document.docx`;
    document.body.appendChild(a);
    a.click();
    a.remove();
  });
```

---

## 스키마 참조 (Schema Reference)

### StudentProfile (학생 프로필)

IEP 파일 생성 시 필요한 20개 필드:

| 필드 | 타입 | 필수 | 설명 | 제약조건 |
|------|------|------|------|----------|
| `name` | string | ✅ | 학생 이름 | 1-100자 |
| `birth` | string | ✅ | 생년월일 | YYYY-MM-DD |
| `grade` | integer | ✅ | 학년 | 1-12 |
| `current_semester` | integer | ✅ | 현재 학기 | 1 or 2 |
| `start_date` | string | ✅ | 학기 시작일 | YYYY-MM-DD |
| `end_date` | string | ✅ | 학기 종료일 | YYYY-MM-DD |
| `guardian_opinion` | string | ✅ | 보호자 의견 | - |
| `cognitive_level` | string | ✅ | 인지 수준 | - |
| `social_psych_level` | string | ✅ | 사회심리 수준 | - |
| `motor_daily_level` | string | ✅ | 운동/일상생활 수준 | - |
| `vci_score` | integer | ✅ | 언어이해지표 (VCI) | 0-200 |
| `visual_spatial_score` | integer | ✅ | 시공간지표 (VSI) | 0-200 |
| `fri_score` | integer | ✅ | 유동추론지표 (FRI) | 0-200 |
| `wmi_score` | integer | ✅ | 작업기억지표 (WMI) | 0-200 |
| `psi_score` | integer | ✅ | 처리속도지표 (PSI) | 0-200 |
| `fsiq_score` | integer | ✅ | 전체 IQ (FSIQ) | 0-200 |
| `korean_performance_level` | string | ✅ | 국어 수행 수준 | - |
| `math_performance_level` | string | ✅ | 수학 수행 수준 | - |
| `korean_domain` | array[string] | ✅ | 국어 학습 영역 | 1-6개 선택 |
| `math_domain` | array[string] | ✅ | 수학 학습 영역 | 1-4개 선택 |

### 국어 도메인 (Korean Domains)

- `listeningSpeaking`: 듣기말하기
- `reading`: 읽기
- `writing`: 쓰기
- `grammar`: 문법
- `literature`: 문학
- `mediaLiteracy`: 매체

### 수학 도메인 (Math Domains)

- `numbersOperations`: 수와 연산
- `changeAndRelations`: 변화와 관계
- `geometryMeasurement`: 도형과 측정
- `dataAndProbability`: 자료와 가능성

---

## 오류 처리 (Error Handling)

### HTTP 상태 코드

| 코드 | 의미 | 설명 |
|------|------|------|
| 200 | OK | 요청 성공 |
| 201 | Created | 리소스 생성 성공 |
| 400 | Bad Request | 잘못된 요청 (유효성 검증 실패) |
| 404 | Not Found | 리소스를 찾을 수 없음 |
| 500 | Internal Server Error | 서버 내부 오류 |

### 오류 응답 형식

```json
{
  "detail": "Error message here"
}
```

### 일반적인 오류 예시

**400 Bad Request - 유효성 검증 실패:**
```json
{
  "detail": [
    {
      "loc": ["body", "grade"],
      "msg": "ensure this value is greater than or equal to 1",
      "type": "value_error.number.not_ge"
    }
  ]
}
```

**404 Not Found - 학생 없음:**
```json
{
  "detail": "Student not found"
}
```

**404 Not Found - IEP 버전 없음:**
```json
{
  "detail": "IEP version not found"
}
```

**404 Not Found - IEP 파일 없음:**
```json
{
  "detail": "IEP file not found"
}
```

**500 Internal Server Error - AI 모듈 오류:**
```json
{
  "detail": "Failed to generate IEP files: AI module error"
}
```

---

## 전체 엔드포인트 요약

| 메서드 | 경로 | 설명 | 인증 |
|--------|------|------|------|
| GET | `/` | 루트 엔드포인트 | ❌ |
| GET | `/health` | 헬스 체크 | ❌ |
| POST | `/students` | 학생 생성 | ❌ |
| GET | `/students` | 학생 목록 조회 | ❌ |
| POST | `/iep-versions` | IEP 버전 생성 | ❌ |
| GET | `/students/{student_id}/iep-latest` | 최신 IEP 조회 | ❌ |
| GET | `/students/{student_id}/iep-versions` | IEP 목록 조회 | ❌ |
| POST | `/iep-files` | IEP 파일 생성 (AI) | ❌ |
| GET | `/iep-versions/{iep_version_id}/iep-files` | IEP 파일 목록 | ❌ |
| GET | `/iep-files/{file_id}/content` | IEP 파일 내용 조회 | ❌ |
| PUT | `/iep-files/{file_id}` | IEP 파일 업데이트 | ❌ |
| GET | `/iep-versions/{iep_version_id}/docx` | DOCX 다운로드 | ❌ |

---

## 사용 시나리오 (Usage Scenarios)

### 시나리오 1: 신규 학생 IEP 생성

```bash
# 1. 학생 생성
STUDENT=$(curl -X POST "http://localhost:8000/students" \
  -H "Content-Type: application/json" \
  -d '{"name": "홍길동", "birth": "2010-03-15"}' | jq -r '.id')

# 2. IEP 버전 생성
IEP_VERSION=$(curl -X POST "http://localhost:8000/iep-versions" \
  -H "Content-Type: application/json" \
  -d "{
    \"student_id\": \"$STUDENT\",
    \"year\": \"2024\",
    \"semester\": \"1학기\",
    \"grade\": \"5\"
  }" | jq -r '.id')

# 3. IEP 파일 생성 (AI)
curl -X POST "http://localhost:8000/iep-files" \
  -H "Content-Type: application/json" \
  -d @student_profile.json

# 4. DOCX 다운로드
curl -X GET "http://localhost:8000/iep-versions/$IEP_VERSION/docx" \
  -o "IEP_홍길동_2024_1학기.docx"
```

### 시나리오 2: 기존 IEP 수정

```bash
# 1. IEP 파일 목록 조회
curl -X GET "http://localhost:8000/iep-versions/$IEP_VERSION/iep-files"

# 2. goals 파일 내용 조회
curl -X GET "http://localhost:8000/iep-files/$FILE_ID/content"

# 3. goals 파일 수정
curl -X PUT "http://localhost:8000/iep-files/$FILE_ID" \
  -H "Content-Type: application/json" \
  -d @updated_goals.json

# 4. 수정된 DOCX 다운로드
curl -X GET "http://localhost:8000/iep-versions/$IEP_VERSION/docx" \
  -o "IEP_홍길동_2024_1학기_수정.docx"
```

---

## 추가 참고 자료

- **[아키텍처 문서](architecture.md)**: 시스템 설계 및 데이터 흐름
- **[개발자 가이드](dev_guide.md)**: 개발 규칙 및 베스트 프랙티스
- **[LLM 프롬프트 사양](../references/llm_prompt_specification.md)**: AI 모듈 인터페이스 상세

---

**최종 업데이트**: 2024-12-26  
**버전**: 1.0.0  
**작성자**: Backend Team

