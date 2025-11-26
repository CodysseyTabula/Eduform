from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.iep_version import IEPVersion
from app.models.student import Student
from app.schemas.iep_version import IEPVersionCreate, IEPVersionResponse

router = APIRouter(tags=["IEP Versions"])


@router.post("/iep-versions", response_model=IEPVersionResponse, status_code=status.HTTP_201_CREATED)
def create_iep_version(
    version_data: IEPVersionCreate,
    db: Session = Depends(get_db),
) -> IEPVersionResponse:
    """
    IEP 버전 생성
    
    - **student_id**: 학생 ID (UUID)
    - **year**: 학년도 (문자열, 예: '2024')
    - **semester**: 학기 (문자열, 예: '1학기', '2학기')
    - **grade**: 학년 스냅샷 (문자열, 예: '3', '4')
    """
    # Validate student exists
    student = db.query(Student).filter(Student.id == version_data.student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Create IEP Version with grade snapshot
    new_version = IEPVersion(
        student_id=version_data.student_id,
        year=version_data.year,
        semester=version_data.semester,
        grade=version_data.grade,
    )
    db.add(new_version)
    db.commit()
    db.refresh(new_version)
    return new_version


@router.get("/students/{student_id}/iep-versions", response_model=list[IEPVersionResponse])
def list_iep_versions(
    student_id: UUID,
    db: Session = Depends(get_db),
) -> list[IEPVersionResponse]:
    """
    학생의 모든 IEP 버전 목록 조회 (최신순)
    
    - **student_id**: 학생 ID (UUID)
    """
    # Validate student exists
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Get all IEP versions for student
    versions = (
        db.query(IEPVersion)
        .filter(IEPVersion.student_id == student_id)
        .order_by(IEPVersion.created_at.desc())
        .all()
    )
    
    return versions


@router.get("/students/{student_id}/iep-latest", response_model=IEPVersionResponse)
def get_latest_iep_version(
    student_id: UUID,
    db: Session = Depends(get_db),
) -> IEPVersionResponse:
    """
    학생의 최신 IEP 버전 조회 (created_at 기준 최신)
    
    - **student_id**: 학생 ID (UUID)
    """
    # Validate student exists
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Get latest IEP version
    latest_version = (
        db.query(IEPVersion)
        .filter(IEPVersion.student_id == student_id)
        .order_by(IEPVersion.created_at.desc())
        .first()
    )
    
    if not latest_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No IEP version found for this student"
        )
    
    return latest_version

