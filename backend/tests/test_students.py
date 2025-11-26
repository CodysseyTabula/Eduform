"""Student 모델 및 API 테스트"""

from __future__ import annotations

import importlib
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app as fastapi_app

# 메타데이터 등록을 위해 모델 모듈을 로드
importlib.import_module("app.models")


@pytest.fixture()
def client():
    """PostgreSQL 전용 TestClient"""
    test_dsn = os.getenv("TEST_DATABASE_URL")
    database_url = test_dsn or settings.sqlalchemy_database_uri

    engine = create_engine(database_url, future=True)
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except OperationalError:
        pytest.skip("PostgreSQL 연결 불가: TEST_DATABASE_URL 또는 기본 DSN 확인 필요")

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    # 테스트 엔진으로 교체해 startup 훅에서도 동일 엔진 사용
    import app.db.session as db_session
    import app.main as main_app

    db_session.engine = engine
    main_app.engine = engine

    fastapi_app.dependency_overrides[get_db] = override_get_db
    with TestClient(fastapi_app) as test_client:
        yield test_client
    fastapi_app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def test_import_student_model():
    """Student 모델 import 테스트"""
    from app.models.student import Student

    assert Student.__tablename__ == "student"
    assert hasattr(Student, "id")
    assert hasattr(Student, "name")
    assert hasattr(Student, "birth")


def test_import_student_schemas():
    """Student 스키마 import 테스트"""
    from app.schemas.student import StudentCreate, StudentResponse

    assert StudentCreate is not None
    assert StudentResponse is not None


def test_import_student_router():
    """Student 라우터 import 테스트"""
    from app.api.students import router

    assert router.prefix == "/students"
    assert "Students" in router.tags


def test_create_student_success(client: TestClient):
    """학생 생성 성공 플로우"""
    payload = {"name": "John Doe", "birth": "2010-05-01"}

    response = client.post("/students", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["birth"] == payload["birth"]
    assert "id" in data and data["id"]


def test_create_student_validation_error(client: TestClient):
    """유효하지 않은 요청 본문은 422를 반환"""
    response = client.post("/students", json={"name": "", "birth": "not-a-date"})

    assert response.status_code == 422
    body = response.json()
    assert "detail" in body


def test_list_students_returns_created_records(client: TestClient):
    """학생 목록 조회가 생성된 데이터를 반환"""
    payloads = [
        {"name": "Alice", "birth": "2011-03-02"},
        {"name": "Bob", "birth": "2012-07-15"},
    ]
    for payload in payloads:
        create_response = client.post("/students", json=payload)
        assert create_response.status_code == 201

    response = client.get("/students")

    assert response.status_code == 200
    students = response.json()
    names = {student["name"] for student in students}
    births = {student["birth"] for student in students}
    assert {"Alice", "Bob"}.issubset(names)
    assert {"2011-03-02", "2012-07-15"}.issubset(births)
