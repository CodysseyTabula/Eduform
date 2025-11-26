from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.student import Student
from app.schemas.student import StudentCreate, StudentResponse

router = APIRouter(prefix="/students", tags=["Students"])


@router.post("", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(
    student_data: StudentCreate,
    db: Session = Depends(get_db),
) -> StudentResponse:
    """
    학생 생성
    
    - **name**: 학생 이름 (1-100자)
    - **birth**: 생년월일 (YYYY-MM-DD)
    """
    new_student = Student(
        name=student_data.name,
        birth=student_data.birth,
    )
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student


@router.get("", response_model=List[StudentResponse])
def list_students(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> List[StudentResponse]:
    """
    학생 목록 조회
    
    - **skip**: 건너뛸 레코드 수 (기본값: 0)
    - **limit**: 최대 반환 레코드 수 (기본값: 100)
    """
    students = db.query(Student).offset(skip).limit(limit).all()
    return students
