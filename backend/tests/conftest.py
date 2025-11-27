"""
Pytest 공유 fixtures 및 테스트 설정

이 파일은 모든 테스트에서 공유되는 fixture를 정의합니다:
- FastAPI TestClient
- 데이터베이스 세션 격리 (트랜잭션 롤백)
- 임시 스토리지 경로
- AI 모듈 모킹
"""
from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import Generator
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# 테스트 환경 강제 설정 (PostgreSQL 연결 회피)
os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("TEST_DATABASE_URL", "sqlite:///:memory:")

from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app


# ==================== 데이터베이스 Fixture ====================

@pytest.fixture(scope="function")
def db_engine():
    """
    테스트용 SQLite 인메모리 데이터베이스 엔진 생성
    
    PostgreSQL 대신 SQLite를 사용하여 테스트 격리 및 속도 향상
    각 테스트 함수마다 새로운 DB 생성
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator[Session, None, None]:
    """
    테스트용 데이터베이스 세션 (트랜잭션 롤백 사용)
    
    각 테스트 후 자동 롤백하여 DB 상태 격리
    """
    connection = db_engine.connect()
    transaction = connection.begin()
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = SessionLocal()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


# ==================== FastAPI Client Fixture ====================

@pytest.fixture(scope="function")
def client(db_session: Session, tmp_storage_path: Path):
    """
    FastAPI TestClient with DB session override
    
    테스트용 DB 세션과 임시 스토리지 경로를 주입한 TestClient
    """
    # Override get_db dependency
    def override_get_db():
        try:
            yield db_session
        finally:
            pass  # Session은 fixture에서 관리
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Override storage path
    original_storage_path = settings.storage_path
    settings.storage_path = str(tmp_storage_path)
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Cleanup
    app.dependency_overrides.clear()
    settings.storage_path = original_storage_path


# ==================== 스토리지 Fixture ====================

@pytest.fixture(scope="function")
def tmp_storage_path(tmp_path: Path) -> Path:
    """
    테스트용 임시 스토리지 경로
    
    각 테스트마다 독립적인 임시 디렉토리 제공
    """
    storage_dir = tmp_path / "storage"
    storage_dir.mkdir(parents=True, exist_ok=True)
    return storage_dir


# ==================== AI 모듈 Mock Fixture ====================

@pytest.fixture(scope="function")
def mock_ai_generators():
    """
    AI 모듈의 generator 함수들을 모킹
    
    실제 OpenAI/Edunet API 호출 없이 테스트용 고정 데이터 반환
    """
    # Mock 데이터: 간단한 IEP 파일 구조
    mock_goals = {
        "reading": {
            "annual_goal": "연간 읽기 목표 (테스트)",
            "semester_goal": "1학기 읽기 목표 (테스트)"
        },
        "numbersOperations": {
            "annual_goal": "연간 수와 연산 목표 (테스트)",
            "semester_goal": "1학기 수와 연산 목표 (테스트)"
        }
    }
    
    mock_weekly_plan = {
        "reading": [
            {"week": i, "content": f"{i}주차 읽기 학습 내용 (테스트)"}
            for i in range(1, 21)
        ],
        "numbersOperations": [
            {"week": i, "content": f"{i}주차 수와 연산 학습 내용 (테스트)"}
            for i in range(1, 21)
        ]
    }
    
    mock_weekly_materials = {
        "reading": [
            {"week": i, "material_url": f"https://example.com/reading/week{i}"}
            for i in range(1, 21)
        ],
        "numbersOperations": [
            {"week": i, "material_url": f"https://example.com/math/week{i}"}
            for i in range(1, 21)
        ]
    }
    
    # AI 모듈 함수들 모킹 (실제 OpenAI 호출 방지)
    with patch("ai_module.generate_goals", return_value=mock_goals), \
         patch("ai_module.generate_weekly_plan", return_value=mock_weekly_plan), \
         patch("ai_module.generate_weekly_materials", return_value=mock_weekly_materials):
        yield {
            "goal": mock_goals,
            "weekly_plan": mock_weekly_plan,
            "material": mock_weekly_materials
        }


# ==================== 테스트 데이터 Helper Fixtures ====================

@pytest.fixture(scope="function")
def sample_student(db_session: Session):
    """
    테스트용 샘플 학생 생성
    """
    from datetime import date
    from app.models.student import Student
    
    student = Student(
        name="테스트학생",
        birth=date(2015, 3, 15)
    )
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)
    
    return student


@pytest.fixture(scope="function")
def sample_iep_version(db_session: Session, sample_student):
    """
    테스트용 샘플 IEP 버전 생성
    """
    from app.models.iep_version import IEPVersion
    
    iep_version = IEPVersion(
        student_id=sample_student.id,
        year="2024",
        semester="1학기",
        grade="3"
    )
    db_session.add(iep_version)
    db_session.commit()
    db_session.refresh(iep_version)
    
    return iep_version


@pytest.fixture(scope="function")
def sample_student_profile():
    """
    테스트용 학생 프로필 데이터 (20개 필드)
    
    IEP 파일 생성 API 요청에 사용
    """
    return {
        # 기본 정보 (4개)
        "name": "테스트학생",
        "birth": "2015-03-15",
        "grade": 3,  # int 타입
        "current_semester": 1,  # int 타입
        
        # IEP 기간 (2개)
        "start_date": "2024-03-01",
        "end_date": "2024-07-31",
        
        # 수행 수준 (4개)
        "guardian_opinion": "학습에 적극적이나 집중력 개선 필요",
        "cognitive_level": "평균 수준",
        "social_psych_level": "또래 관계 원만함",
        "motor_daily_level": "일상생활 독립적",
        
        # 웩슬러 지능검사 (6개)
        "vci_score": 95,
        "visual_spatial_score": 100,
        "fri_score": 90,
        "wmi_score": 88,
        "psi_score": 92,
        "fsiq_score": 93,
        
        # 과목별 수행 수준 (2개)
        "korean_performance_level": "학년 수준",
        "math_performance_level": "학년 수준 약간 미달",
        
        # 도메인 선택 (2개 - 영문 camelCase)
        "korean_domain": ["reading"],  # 영문으로 변경
        "math_domain": ["numbersOperations"]  # 영문으로 변경
    }
