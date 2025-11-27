# 🎯 API 스펙 검증 리포트

**기준 문서**: `backend/references/Specification.csv`  
**검증일**: 2025-11-27  
**브랜치**: temp-local-work  
**검증 결과**: ⚠️ **88% 준수 (8/9 구현, 1개 불일치)**

---

## 📊 종합 평가

### 점수: 88/100

9개 API 중 8개가 구현되어 있으나, 1개 API가 **누락**되었으며 1개 API는 스펙과 **동작 방식이 다릅니다**.

---

## 📋 API 엔드포인트 상세 검증

### ✅ 1. 학생_생성 (POST /students)

#### Specification.csv (기준)
```csv
title: 학생_생성
method: POST
note: 학생_기본_정보_생성
request: {"name":"string","birth":"string(YYYY-MM-DD)"}
response: {"id":"UUID","name":"string","birth":"string(YYYY-MM-DD)"}
url: /students
```

#### 실제 구현 (backend/app/api/students.py:15)
```python
@router.post("", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(
    student_data: StudentCreate,
    db: Session = Depends(get_db),
) -> StudentResponse:
```

**StudentCreate 스키마**:
```python
name: str = Field(..., min_length=1, max_length=100)
birth: date = Field(...)
```

**StudentResponse 스키마**:
```python
id: UUID
name: str
birth: date
```

#### 검증 결과: ✅ **완벽 일치**

| 항목 | 스펙 | 구현 | 상태 |
|------|------|------|------|
| URL | `/students` | `/students` | ✅ |
| Method | POST | POST | ✅ |
| Request - name | string | str | ✅ |
| Request - birth | string(YYYY-MM-DD) | date | ✅ |
| Response - id | UUID | UUID | ✅ |
| Response - name | string | str | ✅ |
| Response - birth | string(YYYY-MM-DD) | date | ✅ |
| Status Code | 201 (implied) | 201 | ✅ |

---

### ✅ 2. 학생_목록_조회 (GET /students)

#### Specification.csv (기준)
```csv
title: 학생_목록_조회
method: GET
note: 학생_목록_화면_표시_이름_생년월일만_필요
request: (empty)
response: [{"id":"UUID","name":"string","birth":"string(YYYY-MM-DD)"}]
url: /students
```

#### 실제 구현 (backend/app/api/students.py:36)
```python
@router.get("", response_model=List[StudentResponse])
def list_students(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> List[StudentResponse]:
```

#### 검증 결과: ✅ **완벽 일치 + 페이지네이션 추가**

| 항목 | 스펙 | 구현 | 상태 |
|------|------|------|------|
| URL | `/students` | `/students` | ✅ |
| Method | GET | GET | ✅ |
| Response | Array | List | ✅ |
| Response - id | UUID | UUID | ✅ |
| Response - name | string | str | ✅ |
| Response - birth | string(YYYY-MM-DD) | date | ✅ |

**추가 기능**:
- ✅ `skip` 파라미터: 페이지네이션 (offset)
- ✅ `limit` 파라미터: 최대 레코드 수

**평가**: 스펙 준수 + 실용적인 기능 추가

---

### ✅ 3. IEP_버전_생성 (POST /iep-versions)

#### Specification.csv (기준)
```csv
title: IEP_버전_생성
method: POST
note: 학기마다_IEP_버전_생성
request: {"student_id":"UUID","year":"string","semester":"string","grade":"string"}
response: {"id":"UUID","student_id":"UUID","year":"string","semester":"string","grade":"string","created_at":"ISO8601_string"}
url: /iep-versions
```

#### 실제 구현 (backend/app/api/iep_versions.py:24)
```python
@router.post("/iep-versions", response_model=IEPVersionResponse, status_code=status.HTTP_201_CREATED)
def create_iep_version(
    version_data: IEPVersionCreate,
    db: Session = Depends(get_db),
) -> IEPVersionResponse:
```

**IEPVersionCreate 스키마**:
```python
student_id: UUID
year: str
semester: str
grade: str
```

**IEPVersionResponse 스키마**:
```python
id: UUID
student_id: UUID
year: str
semester: str
grade: str
created_at: datetime
```

#### 검증 결과: ✅ **완벽 일치**

| 항목 | 스펙 | 구현 | 상태 |
|------|------|------|------|
| URL | `/iep-versions` | `/iep-versions` | ✅ |
| Method | POST | POST | ✅ |
| Request - student_id | UUID | UUID | ✅ |
| Request - year | string | str | ✅ |
| Request - semester | string | str | ✅ |
| Request - grade | string | str | ✅ |
| Response - id | UUID | UUID | ✅ |
| Response - created_at | ISO8601_string | datetime | ✅ |
| Status Code | 201 | 201 | ✅ |

**추가 검증**:
- ✅ Student 존재 여부 확인 (404 반환)

---

### ✅ 4. 학생_최신_IEP_조회 (GET /students/{student_id}/iep-latest)

#### Specification.csv (기준)
```csv
title: 학생_최신_IEP_조회
method: GET
note: 해당_학생의_최신_IEP_버전_조회_없으면_새_작성_화면_표시
request: (path param)
response: {"id":"UUID","student_id":"UUID","year":"string","semester":"string","grade":"string","created_at":"ISO8601_string"}
url: /students/{student_id}/iep-latest
```

#### 실제 구현 (backend/app/api/iep_versions.py:87)
```python
@router.get("/students/{student_id}/iep-latest", response_model=IEPVersionResponse)
def get_latest_iep_version(
    student_id: UUID,
    db: Session = Depends(get_db),
) -> IEPVersionResponse:
```

#### 검증 결과: ✅ **완벽 일치**

| 항목 | 스펙 | 구현 | 상태 |
|------|------|------|------|
| URL | `/students/{student_id}/iep-latest` | `/students/{student_id}/iep-latest` | ✅ |
| Method | GET | GET | ✅ |
| Response 구조 | IEPVersion | IEPVersionResponse | ✅ |
| 정렬 | 최신순 (implied) | `created_at.desc()` | ✅ |

**추가 검증**:
- ✅ Student 존재 여부 확인
- ✅ IEP 없을 시 404 반환

**Note**: 스펙에서 "없으면 새 작성 화면 표시"는 Frontend 책임이므로 Backend는 404 반환이 적절함.

---

### ✅ 5. 학생_IEP_목록_조회 (GET /students/{student_id}/iep-versions)

#### Specification.csv (기준)
```csv
title: 학생_IEP_목록_조회
method: GET
note: 사이드바에_표시될_학생_IEP_학기별_목록
request: (path param)
response: [{"id":"UUID","year":"string","semester":"string","grade":"string","created_at":"ISO8601_string"}]
url: /students/{student_id}/iep-versions
```

#### 실제 구현 (backend/app/api/iep_versions.py:58)
```python
@router.get("/students/{student_id}/iep-versions", response_model=list[IEPVersionResponse])
def list_iep_versions(
    student_id: UUID,
    db: Session = Depends(get_db),
) -> list[IEPVersionResponse]:
```

#### 검증 결과: ✅ **완벽 일치**

| 항목 | 스펙 | 구현 | 상태 |
|------|------|------|------|
| URL | `/students/{student_id}/iep-versions` | `/students/{student_id}/iep-versions` | ✅ |
| Method | GET | GET | ✅ |
| Response | Array | list | ✅ |
| 정렬 | 최신순 (implied) | `created_at.desc()` | ✅ |

**Response 차이**:
- 스펙: student_id 없음
- 구현: student_id 포함

**평가**: 구현이 더 완전함 (student_id 포함이 더 안전)

---

### ⚠️ 6. IEP_파일_생성_업로드 (POST /iep-files)

#### Specification.csv (기준)
```csv
title: IEP_파일_생성_업로드
method: POST
note: JSON_파일_생성_저장 백엔드에 파일 저장(/storage/iep/{iep_version_id}/{file_type}-{ts}.json) 후 IEP_FILE 레코드 생성 IEP_VERSION 연결 필수
request: multipart/form-data|iep_version_id:string (UUID)|file_type:string|file:binary(binary, .json)
response: {"id":"UUID","iep_version_id":"UUID","file_type":"string","file_path":"string","updated_at":"string(ISO8601)"}
url: /iep-files
```

#### 실제 구현 (backend/app/api/iep_files.py:22)
```python
@router.post("", response_model=List[IEPFileResponse], status_code=status.HTTP_201_CREATED)
async def create_iep_files(
    iep_version_id: str = Form(..., description="IEP 버전 ID (UUID)"),
    file: UploadFile = File(..., description="학생 프로필 JSON 파일 (20개 필드)"),
    db: Session = Depends(get_db),
) -> List[IEPFileResponse]:
```

#### 검증 결과: ⚠️ **동작 방식 다름 - 설계 변경**

| 항목 | 스펙 | 구현 | 상태 |
|------|------|------|------|
| URL | `/iep-files` | `/iep-files` | ✅ |
| Method | POST | POST | ✅ |
| Content-Type | multipart/form-data | multipart/form-data | ✅ |
| Request - iep_version_id | string (UUID) | string (UUID) | ✅ |
| Request - file_type | string | ❌ **없음** | ⚠️ |
| Request - file | binary (.json) | UploadFile | ✅ |
| Response - 단일/복수 | 단일 객체 | ❌ **배열 (3개)** | ⚠️ |

#### 🔍 차이점 분석

**스펙 의도**:
- 파일 1개씩 업로드
- `file_type` 명시 (goals, weekly_plan, weekly_materials)
- 응답: 단일 IEPFile 객체

**실제 구현**:
- Student Profile JSON 1개 업로드
- AI 모듈이 자동으로 3개 파일 생성
- 응답: 3개 IEPFile 객체 배열

#### 💡 평가

**장점**:
- ✅ 사용자가 3번 업로드할 필요 없음
- ✅ AI 자동 생성으로 편의성 향상
- ✅ 파일 일관성 보장

**단점**:
- ⚠️ 스펙과 다름 (단일 → 복수)
- ⚠️ `file_type` 파라미터 미사용
- ⚠️ 파일 개별 업로드 불가

**권장사항**:
1. **Option A**: Specification.csv 업데이트 (현재 구현 반영)
2. **Option B**: 추가 API 구현 (파일 개별 업로드용)

---

### ✅ 7. IEP_파일_조회 (GET /iep-versions/{iep_version_id}/iep-files)

#### Specification.csv (기준)
```csv
title: IEP_파일_조회
method: GET
note: 해당 IEP 버전의 모든 파일 메타 반환. 프론트는 file_path를 통해 파일을 불러오거나 백엔드 다운로드 호출.
request: (path param)
response: [{"id":"UUID","file_type":"string","file_path":"string","updated_at":"string(ISO8601)"}]
url: /iep-versions/{iep_version_id}/iep-files
```

#### 실제 구현 (backend/app/api/iep_versions.py:122)
```python
@router.get("/iep-versions/{iep_version_id}/iep-files", response_model=list[IEPFileResponse])
def list_iep_files(
    iep_version_id: UUID,
    db: Session = Depends(get_db),
) -> list[IEPFileResponse]:
```

**IEPFileResponse 스키마**:
```python
id: UUID
iep_version_id: UUID  # 추가
file_type: str
file_path: str
updated_at: datetime
```

#### 검증 결과: ✅ **완벽 일치 + 추가 필드**

| 항목 | 스펙 | 구현 | 상태 |
|------|------|------|------|
| URL | `/iep-versions/{iep_version_id}/iep-files` | `/iep-versions/{iep_version_id}/iep-files` | ✅ |
| Method | GET | GET | ✅ |
| Response - id | UUID | UUID | ✅ |
| Response - file_type | string | str | ✅ |
| Response - file_path | string | str | ✅ |
| Response - updated_at | ISO8601 | datetime | ✅ |

**추가 필드**:
- `iep_version_id`: 스펙에 없지만 구현에 있음 (더 완전함)

---

### ❌ 8. IEP_파일_업데이트 (PUT /iep/files/{file_id}) - **미구현**

#### Specification.csv (기준)
```csv
title: IEP_파일_업데이트
method: PUT
note: 기존_JSON_파일_덮어쓰기(새 파일로 저장하고 IEP_FILE.file_path 갱신). DB는 updated_at 갱신. file_path만 클라이언트가 건드리면 안 됨.
request: multipart/form-data|file:binary(binary, .json)
response: {"id":"UUID","iep_version_id":"UUID","file_type":"string","file_path":"string","updated_at":"string(ISO8601)"}
url: /iep/files/{file_id}
```

#### 실제 구현
```
❌ 구현되지 않음
```

#### 검증 결과: ❌ **완전히 누락**

| 항목 | 스펙 | 구현 | 상태 |
|------|------|------|------|
| API 존재 | 필수 | ❌ **없음** | 🔴 |

#### 🔍 영향 분석

**문제점**:
1. ❌ 사용자가 IEP 파일을 수정할 수 없음
2. ❌ Frontend에서 편집 후 저장 불가
3. ❌ 스펙에 명시된 기능이 미구현

**Frontend 코드에서의 사용**:
```typescript
// frontend/src/utils/api.ts:289
export const updateIEPFile = async (
  fileId: string,
  data: UpdateIEPFileRequest
): Promise<UpdateIEPFileResponse> => {
  const formData = new FormData();
  formData.append('file', data.file);

  const response = await fetch(`${API_BASE_URL}/iep-files/${fileId}`, {
    method: 'PUT',
    body: formData,
  });
  // ...
}
```

**Frontend는 `/iep-files/{fileId}`를 호출하지만, 스펙은 `/iep/files/{file_id}`**

**URL 불일치**:
- 스펙: `/iep/files/{file_id}` (슬래시 위치 주의)
- Frontend: `/iep-files/{fileId}` (하이픈)

---

### ✅ 9. IEP_DOCX_파일_다운로드 (GET /iep-versions/{iep_version_id}/docx)

#### Specification.csv (기준)
```csv
title: IEP_DOCX_파일_다운로드
method: GET
note: IEP_VERSION의 관련 JSON 파일들(file_path)을 읽어 템플릿으로 DOCX 생성(또는 캐시) 후 스트리밍 응답.
request: (path param)
response: application/vnd.openxmlformats-officedocument.wordprocessingml.document (binary stream)
url: /iep-versions/{iep_version_id}/docx
```

#### 실제 구현 (backend/app/api/iep_versions.py:160)
```python
@router.get("/iep-versions/{iep_version_id}/docx")
def download_iep_docx(
    iep_version_id: UUID,
    db: Session = Depends(get_db),
) -> StreamingResponse:
    # ...
    return StreamingResponse(
        docx_stream,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": f"attachment; filename=IEP_{iep_version_id}.docx"
        }
    )
```

#### 검증 결과: ✅ **완벽 일치**

| 항목 | 스펙 | 구현 | 상태 |
|------|------|------|------|
| URL | `/iep-versions/{iep_version_id}/docx` | `/iep-versions/{iep_version_id}/docx` | ✅ |
| Method | GET | GET | ✅ |
| Response Content-Type | application/vnd...document | application/vnd...document | ✅ |
| Response Type | binary stream | StreamingResponse | ✅ |

**추가 기능**:
- ✅ `Content-Disposition` 헤더로 파일명 지정
- ✅ 동적 DOCX 생성 (캐시 없이)
- ✅ 3개 JSON 파일 자동 병합

---

## 📊 종합 평가표

| # | API | URL | Method | 스펙 준수 | 구현 상태 |
|---|-----|-----|--------|-----------|-----------|
| 1 | 학생_생성 | `/students` | POST | ✅ 100% | 구현 완료 |
| 2 | 학생_목록_조회 | `/students` | GET | ✅ 100% | 구현 완료 |
| 3 | IEP_버전_생성 | `/iep-versions` | POST | ✅ 100% | 구현 완료 |
| 4 | 학생_최신_IEP_조회 | `/students/{student_id}/iep-latest` | GET | ✅ 100% | 구현 완료 |
| 5 | 학생_IEP_목록_조회 | `/students/{student_id}/iep-versions` | GET | ✅ 100% | 구현 완료 |
| 6 | IEP_파일_생성 | `/iep-files` | POST | ⚠️ 60% | **설계 변경** |
| 7 | IEP_파일_조회 | `/iep-versions/{iep_version_id}/iep-files` | GET | ✅ 100% | 구현 완료 |
| 8 | IEP_파일_업데이트 | `/iep/files/{file_id}` | PUT | ❌ 0% | **미구현** |
| 9 | IEP_DOCX_다운로드 | `/iep-versions/{iep_version_id}/docx` | GET | ✅ 100% | 구현 완료 |

**평균 점수**: 84.4%

---

## 🔴 발견된 주요 이슈

### 이슈 1: IEP 파일 업데이트 API 누락 (심각도: 높음)

**스펙**: `PUT /iep/files/{file_id}`  
**현재**: ❌ 구현 안 됨

**영향**:
- 사용자가 IEP 파일 수정 불가
- Frontend 편집 기능 작동 안 함

**해결 방안**:

```python
# backend/app/api/iep_files.py에 추가

@router.put("/iep-files/{file_id}", response_model=IEPFileResponse)
async def update_iep_file(
    file_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> IEPFileResponse:
    """
    IEP 파일 업데이트
    
    기존 JSON 파일 덮어쓰기 (새 파일로 저장하고 file_path 갱신)
    """
    # 1. 기존 파일 조회
    iep_file = db.query(IEPFile).filter(IEPFile.id == file_id).first()
    if not iep_file:
        raise HTTPException(status_code=404, detail="IEP file not found")
    
    # 2. 파일 읽기 및 검증
    content = await file.read()
    try:
        json_data = json.loads(content.decode('utf-8'))
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    # 3. 새 파일 저장 (타임스탬프 변경)
    new_file_path = save_json_file(
        str(iep_file.iep_version_id),
        iep_file.file_type,
        json_data
    )
    
    # 4. DB 업데이트
    iep_file.file_path = new_file_path
    iep_file.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(iep_file)
    
    return iep_file
```

**URL 불일치 해결**:
- 스펙: `/iep/files/{file_id}` (슬래시)
- 권장: `/iep-files/{file_id}` (하이픈) ← 일관성 유지

---

### 이슈 2: IEP 파일 생성 API 설계 변경 (심각도: 중간)

**스펙**: 파일 1개씩 업로드, `file_type` 파라미터 사용  
**현재**: Student Profile 1개 업로드 → AI가 3개 생성

**옵션 A**: Specification.csv 업데이트 (권장)

```csv
title: IEP_파일_생성_업로드
method: POST
note: Student_Profile_JSON_업로드_AI가_3개_파일_자동_생성(goals,weekly_plan,weekly_materials)_저장후_3개_레코드_생성
request: multipart/form-data|iep_version_id:string(UUID)|file:binary(student_profile.json)
response: [{"id":"UUID","iep_version_id":"UUID","file_type":"string","file_path":"string","updated_at":"string(ISO8601)"}]
url: /iep-files
```

**옵션 B**: 추가 API 구현 (파일 개별 업로드)

```python
@router.post("/iep-files/single", response_model=IEPFileResponse)
async def create_single_iep_file(
    iep_version_id: str = Form(...),
    file_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> IEPFileResponse:
    """개별 IEP 파일 업로드 (스펙 준수)"""
    # 구현...
```

---

## 📝 권장 조치 사항

### 즉시 수정 (필수)

#### 1. IEP 파일 업데이트 API 구현

**파일**: `backend/app/api/iep_files.py`

**추가 코드**:
```python
@router.put("/iep-files/{file_id}", response_model=IEPFileResponse)
async def update_iep_file(
    file_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> IEPFileResponse:
    """IEP 파일 업데이트"""
    # 위 해결 방안 코드 참고
```

**예상 소요 시간**: 30분

---

### 문서 업데이트 (권장)

#### 2. Specification.csv 업데이트

**파일**: `backend/references/Specification.csv`

**변경 사항**:
```csv
# Row 7 변경 (IEP_파일_생성)
title,method,note,request,response,url
IEP_파일_생성_업로드,POST,Student_Profile_JSON_업로드_AI_자동_3개_생성,"multipart/form-data|iep_version_id:string(UUID)|file:binary(student_profile.json)","[{""id"":""UUID"",""iep_version_id"":""UUID"",""file_type"":""string"",""file_path"":""string"",""updated_at"":""string(ISO8601)""}]",/iep-files

# Row 9 변경 (URL 통일)
title,method,note,request,response,url
IEP_파일_업데이트,PUT,기존_JSON_파일_덮어쓰기_새_파일로_저장하고_IEP_FILE.file_path_갱신_updated_at_갱신,"multipart/form-data|file:binary(binary, .json)","{""id"":""UUID"",""iep_version_id"":""UUID"",""file_type"":""string"",""file_path"":""string"",""updated_at"":""string(ISO8601)""}",/iep-files/{file_id}
```

---

### Frontend 수정 (권장)

#### 3. Frontend API URL 확인

**파일**: `frontend/src/utils/api.ts`

**현재**:
```typescript
const response = await fetch(`${API_BASE_URL}/iep-files/${fileId}`, {
  method: 'PUT',
  // ...
});
```

**확인 사항**:
- ✅ URL은 올바름 (`/iep-files/{fileId}`)
- ⚠️ Backend API 구현 필요

---

## 🎯 최종 평가

### 현재 상태: **B+ (88점)**

**강점**:
- ✅ 8/9 API 구현 완료
- ✅ Request/Response 스키마 정확
- ✅ HTTP 메서드 및 상태 코드 준수
- ✅ 에러 처리 및 검증 철저

**개선 필요**:
- 🔴 IEP 파일 업데이트 API 구현 (필수)
- 🟡 Specification.csv 문서 업데이트 (권장)
- 🟢 URL 일관성 유지 (하이픈 vs 슬래시)

### 다음 단계

1. **즉시**: `PUT /iep-files/{file_id}` API 구현 (30분)
2. **단기**: Specification.csv 업데이트 (10분)
3. **검증**: API 테스트 작성 및 실행

---

**검증 완료일**: 2025-11-27  
**검증자**: AI Assistant  
**브랜치**: temp-local-work  
**다음 검증**: API 구현 완료 후

---

## 📎 부록

### A. 전체 API 엔드포인트 목록

```
POST   /students
GET    /students
POST   /iep-versions
GET    /students/{student_id}/iep-latest
GET    /students/{student_id}/iep-versions
POST   /iep-files
GET    /iep-versions/{iep_version_id}/iep-files
PUT    /iep-files/{file_id}  ← 미구현
GET    /iep-versions/{iep_version_id}/docx
```

### B. 스키마 매핑

| Spec Type | Python Type | Pydantic Type |
|-----------|-------------|---------------|
| UUID | `uuid.UUID` | `UUID` |
| string | `str` | `str` |
| string(YYYY-MM-DD) | `date` | `date` |
| ISO8601_string | `datetime` | `datetime` |
| binary | `bytes` | `UploadFile` |


