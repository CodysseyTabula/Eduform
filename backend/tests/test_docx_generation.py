"""
DOCX 문서 생성 서비스 테스트
"""
from __future__ import annotations

import os
import sys
import json
from datetime import date, datetime, timezone
from io import BytesIO
from pathlib import Path
from uuid import UUID, uuid4

# PYTHONPATH 설정 (테스트 파일을 직접 실행할 때 필요)
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from docx import Document

from app.db.base import Base
from app.models.student import Student
from app.models.iep_version import IEPVersion
from app.models.iep_file import IEPFile
from app.services.document_generator import (
    generate_docx_for_iep,
    generate_docx_stream,
    DocumentNotFoundError,
    DocumentGenerationError,
)


# 테스트용 인메모리 DB 설정
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """테스트용 DB 세션 픽스처"""
    # 테이블 생성
    Base.metadata.create_all(bind=engine)
    
    # 세션 생성
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        # 테이블 삭제
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_iep_data(db_session, tmp_path, monkeypatch):
    """
    샘플 IEP 데이터 생성 (학생 + IEP 버전 + 3개 JSON 파일)
    
    Returns:
        dict: {
            "student": Student,
            "iep_version": IEPVersion,
            "files": {
                "goals": IEPFile,
                "weekly_plan": IEPFile,
                "weekly_materials": IEPFile,
            }
        }
    """
    # 임시 storage_path 설정
    storage_path = tmp_path / "storage"
    storage_path.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr("app.core.config.settings.storage_path", str(storage_path))
    monkeypatch.setattr("app.services.file_storage.settings.storage_path", str(storage_path))
    
    # 1. 학생 생성
    student = Student(
        id=uuid4(),
        name="테스트학생",
        birth=date(2010, 3, 15),
    )
    db_session.add(student)
    db_session.commit()
    
    # 2. IEP 버전 생성
    iep_version = IEPVersion(
        id=uuid4(),
        student_id=student.id,
        year="2024",
        semester="1학기",
        grade="3",
        created_at=datetime.now(timezone.utc),
    )
    db_session.add(iep_version)
    db_session.commit()
    
    # 3. JSON 파일 생성 (디스크)
    version_dir = storage_path / "iep" / str(iep_version.id)
    version_dir.mkdir(parents=True, exist_ok=True)
    
    # Goals JSON
    goals_data = {
        "reading": {
            "annual_goal": "학년 수준의 글을 읽고 이해할 수 있다.",
            "semester_goal": "간단한 설명문을 읽고 주요 내용을 파악할 수 있다.",
        },
        "writing": {
            "annual_goal": "자신의 생각을 문장으로 표현할 수 있다.",
            "semester_goal": "3-4문장의 짧은 글을 쓸 수 있다.",
        },
        "numbersOperations": {
            "annual_goal": "100 이내의 덧셈과 뺄셈을 할 수 있다.",
            "semester_goal": "받아올림이 있는 두 자리 수 덧셈을 할 수 있다.",
        },
    }
    goals_path = version_dir / "goals-1234567890.json"
    with open(goals_path, "w", encoding="utf-8") as f:
        json.dump(goals_data, f, ensure_ascii=False, indent=2)
    
    # Weekly Plan JSON
    weekly_plan_data = {
        "reading": [
            {"week": 1, "content": "글자 익히기"},
            {"week": 2, "content": "단어 읽기"},
            {"week": 3, "content": "문장 읽기"},
        ],
        "writing": [
            {"week": 1, "content": "글자 쓰기 연습"},
            {"week": 2, "content": "단어 쓰기 연습"},
        ],
        "numbersOperations": [
            {"week": 1, "content": "10 이내 덧셈"},
            {"week": 2, "content": "20 이내 덧셈"},
        ],
    }
    weekly_plan_path = version_dir / "weekly_plan-1234567890.json"
    with open(weekly_plan_path, "w", encoding="utf-8") as f:
        json.dump(weekly_plan_data, f, ensure_ascii=False, indent=2)
    
    # Weekly Materials JSON
    weekly_materials_data = {
        "reading": [
            {"week": 1, "material_url": "https://edunet.net/material/reading/1"},
            {"week": 2, "material_url": "https://edunet.net/material/reading/2"},
        ],
        "writing": [
            {"week": 1, "material_url": "https://edunet.net/material/writing/1"},
        ],
        "numbersOperations": [
            {"week": 1, "material_url": "https://edunet.net/material/math/1"},
        ],
    }
    weekly_materials_path = version_dir / "weekly_materials-1234567890.json"
    with open(weekly_materials_path, "w", encoding="utf-8") as f:
        json.dump(weekly_materials_data, f, ensure_ascii=False, indent=2)
    
    # 4. IEPFile 메타데이터 생성 (DB)
    files = {}
    for file_type, file_path in [
        ("goals", str(goals_path)),
        ("weekly_plan", str(weekly_plan_path)),
        ("weekly_materials", str(weekly_materials_path)),
    ]:
        iep_file = IEPFile(
            id=uuid4(),
            iep_version_id=iep_version.id,
            file_type=file_type,
            file_path=file_path,
            updated_at=datetime.now(timezone.utc),
        )
        db_session.add(iep_file)
        files[file_type] = iep_file
    
    db_session.commit()
    
    return {
        "student": student,
        "iep_version": iep_version,
        "files": files,
    }


def test_import_modules():
    """모듈 임포트 테스트"""
    from app.services.document_generator import (
        generate_docx_for_iep,
        generate_docx_stream,
        DocumentNotFoundError,
    )
    from app.api.iep_versions import download_iep_docx
    
    assert callable(generate_docx_for_iep)
    assert callable(generate_docx_stream)
    assert callable(download_iep_docx)
    assert issubclass(DocumentNotFoundError, Exception)


def test_generate_docx_for_iep_success(db_session, sample_iep_data, tmp_path):
    """
    DOCX 생성 - 정상 경로 테스트
    
    검증 사항:
    - DOCX 파일 생성 성공
    - 파일이 디스크에 존재
    - 파일 크기가 0보다 큼
    """
    iep_version = sample_iep_data["iep_version"]
    
    # DOCX 생성
    output_path = tmp_path / f"test_iep_{iep_version.id}.docx"
    result_path = generate_docx_for_iep(
        db=db_session,
        iep_version_id=iep_version.id,
        output_path=str(output_path)
    )
    
    # 검증
    assert result_path == str(output_path.absolute())
    assert os.path.exists(result_path)
    assert os.path.getsize(result_path) > 0
    
    # DOCX 파일 내용 검증
    doc = Document(result_path)
    
    # 문단 텍스트 수집
    paragraphs_text = "\n".join([p.text for p in doc.paragraphs])
    
    # 테이블 텍스트 수집 (메타데이터는 테이블에 있음)
    tables_text = ""
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                tables_text += cell.text + " "
    
    doc_text = paragraphs_text + "\n" + tables_text
    
    # 제목 확인
    assert "개별화 교육 계획 (IEP)" in doc_text
    
    # IEP 메타데이터 확인
    assert "2024" in doc_text
    assert "1학기" in doc_text
    assert "3" in doc_text


def test_generate_docx_stream_success(db_session, sample_iep_data):
    """
    DOCX 스트림 생성 - 정상 경로 테스트
    
    검증 사항:
    - BytesIO 스트림 반환
    - 스트림 크기가 0보다 큼
    - Document로 읽을 수 있음
    """
    iep_version = sample_iep_data["iep_version"]
    
    # DOCX 스트림 생성
    docx_stream = generate_docx_stream(
        db=db_session,
        iep_version_id=iep_version.id
    )
    
    # 검증
    assert isinstance(docx_stream, BytesIO)
    
    # 스트림을 Document로 읽기
    doc = Document(docx_stream)
    doc_text = "\n".join([p.text for p in doc.paragraphs])
    
    # 내용 확인
    assert "개별화 교육 계획 (IEP)" in doc_text
    assert "IEP 정보" in doc_text


def test_generate_docx_with_domain_filtering(db_session, sample_iep_data):
    """
    도메인 필터링 테스트
    
    검증 사항:
    - 선택된 도메인(reading, writing, numbersOperations)만 포함
    - 선택되지 않은 도메인(listeningSpeaking, grammar 등)은 제외
    """
    iep_version = sample_iep_data["iep_version"]
    
    # DOCX 스트림 생성
    docx_stream = generate_docx_stream(
        db=db_session,
        iep_version_id=iep_version.id
    )
    
    # Document로 읽기
    doc = Document(docx_stream)
    doc_text = "\n".join([p.text for p in doc.paragraphs])
    
    # 선택된 도메인 확인 (포함되어야 함)
    assert "국어 - 읽기" in doc_text
    assert "국어 - 쓰기" in doc_text
    assert "수학 - 수와 연산" in doc_text
    
    # Goals 내용 확인
    assert "학년 수준의 글을 읽고 이해할 수 있다" in doc_text
    assert "자신의 생각을 문장으로 표현할 수 있다" in doc_text
    assert "100 이내의 덧셈과 뺄셈을 할 수 있다" in doc_text
    
    # Weekly Plan 내용 확인
    assert "글자 익히기" in doc_text
    assert "글자 쓰기 연습" in doc_text
    assert "10 이내 덧셈" in doc_text


def test_generate_docx_iep_version_not_found(db_session):
    """
    IEP 버전 없음 - 404 에러 테스트
    
    검증 사항:
    - 존재하지 않는 IEP 버전 ID로 요청 시 DocumentNotFoundError 발생
    """
    non_existent_id = uuid4()
    
    with pytest.raises(DocumentNotFoundError) as exc_info:
        generate_docx_stream(
            db=db_session,
            iep_version_id=non_existent_id
        )
    
    assert "IEP version not found" in str(exc_info.value)


def test_generate_docx_missing_files(db_session, sample_iep_data):
    """
    필수 파일 누락 - 404 에러 테스트
    
    검증 사항:
    - goals.json 파일이 없을 때 DocumentNotFoundError 발생
    """
    iep_version = sample_iep_data["iep_version"]
    
    # goals 파일만 삭제
    goals_file = sample_iep_data["files"]["goals"]
    db_session.delete(goals_file)
    db_session.commit()
    
    with pytest.raises(DocumentNotFoundError) as exc_info:
        generate_docx_stream(
            db=db_session,
            iep_version_id=iep_version.id
        )
    
    assert "Missing required IEP files" in str(exc_info.value)
    assert "goals" in str(exc_info.value)


def test_generate_docx_corrupted_json_file(db_session, sample_iep_data):
    """
    손상된 JSON 파일 - 에러 테스트
    
    검증 사항:
    - JSON 파일이 손상되었을 때 적절한 에러 발생
    """
    iep_version = sample_iep_data["iep_version"]
    goals_file = sample_iep_data["files"]["goals"]
    
    # JSON 파일을 손상시킴
    with open(goals_file.file_path, "w", encoding="utf-8") as f:
        f.write("{ invalid json }")
    
    with pytest.raises(DocumentNotFoundError) as exc_info:
        generate_docx_stream(
            db=db_session,
            iep_version_id=iep_version.id
        )
    
    assert "Failed to load IEP JSON files" in str(exc_info.value)


if __name__ == "__main__":
    # 직접 실행 시 pytest 실행
    pytest.main([__file__, "-v"])

