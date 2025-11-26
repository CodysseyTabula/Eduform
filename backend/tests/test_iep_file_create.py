"""
IEP 파일 생성 API 통합 테스트
"""
from __future__ import annotations

import os
import sys
import json
from datetime import date
from uuid import uuid4
from pathlib import Path

# PYTHONPATH 설정 (테스트 파일을 직접 실행할 때 필요)
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models.student import Student
from app.models.iep_version import IEPVersion
from app.models.iep_file import IEPFile
from app.services.ai_integration import create_iep_files_with_ai


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
def sample_student_profile():
    """샘플 학생 프로필 (20개 필드)"""
    return {
        "name": "테스트학생",
        "birth": "2010-03-15",
        "grade": 3,
        "current_semester": 1,
        "start_date": "2024-03-01",
        "end_date": "2024-08-31",
        "guardian_opinion": "수학 영역 보충이 필요합니다.",
        "cognitive_level": "보통",
        "social_psych_level": "양호",
        "motor_daily_level": "양호",
        "vci_score": 95,
        "visual_spatial_score": 88,
        "fri_score": 92,
        "wmi_score": 85,
        "psi_score": 90,
        "fsiq_score": 90,
        "korean_performance_level": "보통",
        "math_performance_level": "미흡",
        "korean_domain": ["reading", "writing"],
        "math_domain": ["numbersOperations"]
    }


def test_import_modules():
    """모듈 임포트 테스트"""
    from app.api.iep_files import router
    from app.services.ai_integration import create_iep_files_with_ai
    from app.schemas.iep_file import IEPFileCreateRequest
    from app.schemas.student_profile import StudentProfile
    
    assert router.prefix == "/iep-files"
    assert callable(create_iep_files_with_ai)


def test_create_iep_files_with_ai(db_session, sample_student_profile, tmp_path, monkeypatch):
    """
    AI 통합 서비스 - IEP 파일 생성 테스트
    
    검증 사항:
    - AI 모듈 호출 성공
    - 3개 JSON 파일 디스크 저장
    - 3개 IEPFile 메타데이터 DB 저장
    """
    # 임시 storage_path 설정
    storage_path = tmp_path / "storage"
    storage_path.mkdir()
    
    # settings.storage_path를 임시 경로로 변경
    from app.core import config
    monkeypatch.setattr(config.settings, "storage_path", str(storage_path))
    
    # 1. 테스트용 Student, IEPVersion 생성
    student = Student(
        name="테스트학생",
        birth=date(2010, 3, 15)
    )
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)
    
    iep_version = IEPVersion(
        student_id=student.id,
        year="2024",
        semester="1학기",
        grade="3"
    )
    db_session.add(iep_version)
    db_session.commit()
    db_session.refresh(iep_version)
    
    # 2. IEP 파일 생성 (AI 서비스 호출)
    iep_files = create_iep_files_with_ai(
        iep_version_id=iep_version.id,
        student_profile=sample_student_profile,
        db=db_session
    )
    
    # 3. 검증: 3개 파일 레코드 생성 확인
    assert len(iep_files) == 3
    
    file_types = {f.file_type for f in iep_files}
    assert file_types == {"goals", "weekly_plan", "weekly_materials"}
    
    # 4. 검증: DB에 3개 레코드 저장 확인
    db_records = db_session.query(IEPFile).filter(
        IEPFile.iep_version_id == iep_version.id
    ).all()
    assert len(db_records) == 3
    
    # 5. 검증: 디스크에 파일 저장 확인
    for iep_file in iep_files:
        assert os.path.exists(iep_file.file_path), f"파일이 존재하지 않습니다: {iep_file.file_path}"
        
        # JSON 파일 읽기
        with open(iep_file.file_path, 'r', encoding='utf-8') as f:
            content = json.load(f)
        
        assert isinstance(content, dict), "JSON 컨텐츠는 dict 타입이어야 합니다"
        assert len(content) > 0, "JSON 컨텐츠가 비어있습니다"
    
    print("✅ 통합 테스트 통과: IEP 파일 생성 성공")


def test_student_profile_schema():
    """StudentProfile 스키마 검증 테스트"""
    from app.schemas.student_profile import StudentProfile
    
    # 유효한 데이터
    valid_data = {
        "name": "홍길동",
        "birth": "2010-05-20",
        "grade": 3,
        "current_semester": 1,
        "start_date": "2024-03-01",
        "end_date": "2024-08-31",
        "guardian_opinion": "수학 보충 필요",
        "cognitive_level": "보통",
        "social_psych_level": "양호",
        "motor_daily_level": "양호",
        "vci_score": 95,
        "visual_spatial_score": 88,
        "fri_score": 92,
        "wmi_score": 85,
        "psi_score": 90,
        "fsiq_score": 90,
        "korean_performance_level": "보통",
        "math_performance_level": "미흡",
        "korean_domain": ["reading"],
        "math_domain": ["numbersOperations"]
    }
    
    profile = StudentProfile(**valid_data)
    assert profile.name == "홍길동"
    assert profile.grade == 3
    assert len(profile.korean_domain) == 1
    assert len(profile.math_domain) == 1
    
    print("✅ StudentProfile 스키마 검증 통과")


def test_iep_file_create_request_schema():
    """IEPFileCreateRequest 스키마 검증 테스트"""
    from app.schemas.iep_file import IEPFileCreateRequest
    from app.schemas.student_profile import StudentProfile
    
    profile_data = {
        "name": "홍길동",
        "birth": "2010-05-20",
        "grade": 3,
        "current_semester": 1,
        "start_date": "2024-03-01",
        "end_date": "2024-08-31",
        "guardian_opinion": "수학 보충 필요",
        "cognitive_level": "보통",
        "social_psych_level": "양호",
        "motor_daily_level": "양호",
        "vci_score": 95,
        "visual_spatial_score": 88,
        "fri_score": 92,
        "wmi_score": 85,
        "psi_score": 90,
        "fsiq_score": 90,
        "korean_performance_level": "보통",
        "math_performance_level": "미흡",
        "korean_domain": ["reading"],
        "math_domain": ["numbersOperations"]
    }
    
    request_data = {
        "iep_version_id": str(uuid4()),
        "student_profile": profile_data
    }
    
    request = IEPFileCreateRequest(**request_data)
    assert isinstance(request.student_profile, StudentProfile)
    assert request.student_profile.name == "홍길동"
    
    print("✅ IEPFileCreateRequest 스키마 검증 통과")


if __name__ == "__main__":
    """로컬 실행용 (pytest 없이)"""
    print("🧪 IEP 파일 생성 API 테스트 시작\n")
    
    # Import level 테스트
    print("1. Import level 테스트...")
    test_import_modules()
    print("   ✅ 모듈 임포트 성공\n")
    
    # 스키마 테스트
    print("2. StudentProfile 스키마 테스트...")
    test_student_profile_schema()
    print()
    
    print("3. IEPFileCreateRequest 스키마 테스트...")
    test_iep_file_create_request_schema()
    print()
    
    print("✅ 모든 테스트 통과!")

