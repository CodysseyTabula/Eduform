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
# create_iep_files_with_ai 함수는 제거됨 (file_type별로 1개씩 생성하는 방식으로 변경)


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
    from app.schemas.iep_file import IEPFileCreateRequest
    from app.schemas.student_profile import StudentProfile
    
    assert router.prefix == "/iep-files"


# test_create_iep_files_with_ai 함수는 제거됨
# 현재는 file_type별로 1개씩 생성하는 방식이므로 API 엔드포인트 테스트로 대체됨


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
