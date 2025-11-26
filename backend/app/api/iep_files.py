"""
IEP 파일 생성 API 라우터
"""
from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.iep_version import IEPVersion
from app.schemas.iep_file import IEPFileCreateRequest, IEPFileResponse
from app.services.ai_integration import create_iep_files_with_ai, AIIntegrationError

router = APIRouter(prefix="/iep-files", tags=["IEP Files"])


@router.post("", response_model=List[IEPFileResponse], status_code=status.HTTP_201_CREATED)
def create_iep_files(
    request: IEPFileCreateRequest,
    db: Session = Depends(get_db),
) -> List[IEPFileResponse]:
    """
    IEP 파일 생성 (AI 모듈 사용)
    
    **프로세스:**
    1. IEP Version 존재 여부 검증
    2. student_profile을 AI 모듈로 전달
    3. AI 모듈이 3개 JSON 생성 (goals, weekly_plan, weekly_materials)
    4. 3개 파일을 디스크에 저장
    5. 3개 파일의 메타데이터를 DB에 저장
    
    **요청 필드:**
    - **iep_version_id**: IEP 버전 ID (UUID)
    - **student_profile**: 학생 프로필 (20개 필드)
    
    **응답:**
    - 생성된 3개 IEP 파일 메타데이터 리스트
    
    **에러 응답:**
    - 404: IEP version not found
    - 500: AI 모듈 호출 실패 또는 파일 저장 실패
    """
    # 1. IEP Version 존재 검증
    iep_version = db.query(IEPVersion).filter(
        IEPVersion.id == request.iep_version_id
    ).first()
    
    if not iep_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="IEP version not found"
        )
    
    # 2. student_profile을 dict로 변환하여 AI 서비스 호출
    try:
        profile_dict = request.student_profile.model_dump()
        iep_files = create_iep_files_with_ai(
            iep_version_id=request.iep_version_id,
            student_profile=profile_dict,
            db=db
        )
    except AIIntegrationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )
    
    # 3. 생성된 3개 파일 메타데이터 반환
    return iep_files

