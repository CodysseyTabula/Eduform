"""
IEP 파일 생성 API 라우터
"""
from __future__ import annotations

import json
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.iep_version import IEPVersion
from app.schemas.iep_file import IEPFileResponse
from app.schemas.student_profile import StudentProfile
from app.services.ai_integration import create_iep_files_with_ai, AIIntegrationError

router = APIRouter(prefix="/iep-files", tags=["IEP Files"])


@router.post("", response_model=List[IEPFileResponse], status_code=status.HTTP_201_CREATED)
async def create_iep_files(
    iep_version_id: str = Form(..., description="IEP 버전 ID (UUID)"),
    file: UploadFile = File(..., description="학생 프로필 JSON 파일 (20개 필드)"),
    db: Session = Depends(get_db),
) -> List[IEPFileResponse]:
    """
    IEP 파일 생성 (AI 모듈 사용)
    
    **프로세스:**
    1. multipart/form-data로 student_profile JSON 파일 수신
    2. IEP Version 존재 여부 검증
    3. student_profile을 AI 모듈로 전달
    4. AI 모듈이 3개 JSON 생성 (goals, weekly_plan, weekly_materials)
    5. 3개 파일을 디스크에 저장
    6. 3개 파일의 메타데이터를 DB에 저장
    
    **요청 (multipart/form-data):**
    - **iep_version_id**: IEP 버전 ID (UUID)
    - **file**: 학생 프로필 JSON 파일 (20개 필드)
    
    **응답:**
    - 생성된 3개 IEP 파일 메타데이터 리스트
    
    **에러 응답:**
    - 400: JSON 파일 형식 오류 또는 Validation 실패
    - 404: IEP version not found
    - 500: AI 모듈 호출 실패 또는 파일 저장 실패
    """
    # 1. UUID 파싱
    try:
        iep_version_uuid = UUID(iep_version_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID format for iep_version_id"
        )
    
    # 2. IEP Version 존재 검증
    iep_version = db.query(IEPVersion).filter(
        IEPVersion.id == iep_version_uuid
    ).first()
    
    if not iep_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="IEP version not found"
        )
    
    # 3. 업로드된 JSON 파일 읽기 및 파싱
    try:
        content = await file.read()
        profile_data = json.loads(content.decode('utf-8'))
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON file format"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read uploaded file: {str(e)}"
        )
    
    # 4. StudentProfile 스키마 검증
    try:
        student_profile = StudentProfile(**profile_data)
        profile_dict = student_profile.model_dump()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid student profile data: {str(e)}"
        )
    
    # 5. AI 서비스 호출
    try:
        iep_files = create_iep_files_with_ai(
            iep_version_id=iep_version_uuid,
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
    
    # 6. 생성된 3개 파일 메타데이터 반환
    return iep_files


