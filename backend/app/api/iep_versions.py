from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.iep_file import IEPFile
from app.models.iep_version import IEPVersion
from app.models.student import Student
from app.schemas.iep_file import IEPFileResponse
from app.schemas.iep_version import IEPVersionCreate, IEPVersionResponse
from app.services.document_generator import (
    generate_docx_stream,
    DocumentNotFoundError,
    DocumentGenerationError,
)

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


@router.get("/iep-versions/{iep_version_id}/iep-files", response_model=list[IEPFileResponse])
def list_iep_files(
    iep_version_id: UUID,
    db: Session = Depends(get_db),
) -> list[IEPFileResponse]:
    """
    IEP 버전의 모든 파일 메타데이터 조회
    
    - **iep_version_id**: IEP 버전 ID (UUID)
    
    Returns:
        list[IEPFileResponse]: IEP 파일 메타데이터 리스트
    
    Raises:
        404: IEP 버전이 존재하지 않을 때
    """
    # IEP 버전 존재 확인
    iep_version = db.query(IEPVersion).filter(
        IEPVersion.id == iep_version_id
    ).first()
    
    if not iep_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="IEP version not found"
        )
    
    # IEP 파일 조회
    iep_files = (
        db.query(IEPFile)
        .filter(IEPFile.iep_version_id == iep_version_id)
        .order_by(IEPFile.updated_at.desc())
        .all()
    )
    
    return iep_files


@router.get("/iep-versions/{iep_version_id}/docx")
def download_iep_docx(
    iep_version_id: UUID,
    db: Session = Depends(get_db),
) -> StreamingResponse:
    """
    IEP DOCX 파일 다운로드
    
    IEP 버전의 3개 JSON 파일(goals, weekly_plan, weekly_materials)을 읽어
    DOCX 문서를 동적으로 생성하고 다운로드를 제공합니다.
    
    - **iep_version_id**: IEP 버전 ID (UUID)
    
    Returns:
        StreamingResponse: DOCX 파일 스트림
        - Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document
        - Content-Disposition: attachment; filename=IEP_{iep_version_id}.docx
    
    Raises:
        404: IEP 버전이나 필수 파일(goals, weekly_plan, weekly_materials)이 없을 때
        500: 문서 생성 중 오류 발생 시
    """
    try:
        # DOCX 스트림 생성
        docx_stream = generate_docx_stream(db, iep_version_id)
        
        # StreamingResponse로 다운로드 제공
        return StreamingResponse(
            docx_stream,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename=IEP_{iep_version_id}.docx"
            }
        )
    
    except DocumentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DocumentGenerationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate DOCX: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )

