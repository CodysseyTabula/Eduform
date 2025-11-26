"""Student 모델 및 API 테스트"""

from __future__ import annotations


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
