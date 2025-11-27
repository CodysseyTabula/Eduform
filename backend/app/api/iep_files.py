"""
IEP 파일 생성/수정 API 라우터
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.iep_file import IEPFile
from app.models.iep_version import IEPVersion
from app.schemas.iep_file import IEPFileResponse
from app.schemas.student_profile import StudentProfile
from app.services.file_storage import save_json_file, FileStorageError

router = APIRouter(prefix="/iep-files", tags=["IEP Files"])


@router.post("", response_model=IEPFileResponse, status_code=status.HTTP_201_CREATED)
async def create_iep_file(
    iep_version_id: str = Form(..., description="IEP 버전 ID (UUID)"),
    file_type: str = Form(..., description="파일 타입 (student_info, goal, weekly_content, weekly_material)"),
    file: UploadFile = File(..., description="학생 프로필 JSON 파일 (20개 필드)"),
    db: Session = Depends(get_db),
) -> IEPFileResponse:
    """
    IEP 파일 생성 (AI 모듈 사용)
    
    사용자가 file_type을 선택하여 해당 타입의 IEP 파일 1개를 생성합니다.
    4개 파일(student_info, goal, weekly_content, weekly_material)을 모두 만들려면 이 API를 호출해야 합니다.
    
    **프로세스:**
    1. multipart/form-data로 student_profile JSON 파일 수신
    2. IEP Version 존재 여부 검증
    3. file_type에 따라 해당 AI 함수 호출
       - "student_info" → 업로드된 프로필을 그대로 저장
       - "goal" → generate_goals()
       - "weekly_content" → generate_weekly_plan()
       - "weekly_material" → generate_weekly_materials()
    4. 생성된 JSON을 디스크에 저장
    5. IEP_FILE 레코드 DB에 저장
    
    **요청 (multipart/form-data):**
    - **iep_version_id**: IEP 버전 ID (UUID)
    - **file_type**: "student_info", "goal", "weekly_content", "weekly_material" 중 하나 선택
    - **file**: 학생 프로필 JSON 파일 (20개 필드)
    
    **응답:**
    - 생성된 IEP 파일 메타데이터 (단일 객체)
    
    **에러 응답:**
    - 400: JSON 형식 오류, Validation 실패, 잘못된 file_type
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
    
    # 2. file_type 검증
    valid_file_types = ["student_info", "goal", "weekly_content", "weekly_material"]
    if file_type not in valid_file_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file_type. Must be one of: {', '.join(valid_file_types)}"
        )
    
    # 3. IEP Version 존재 검증
    iep_version = db.query(IEPVersion).filter(
        IEPVersion.id == iep_version_uuid
    ).first()
    
    if not iep_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="IEP version not found"
        )
    
    # 4. 업로드된 JSON 파일 읽기 및 파싱
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
    
    # 5. StudentProfile 스키마 검증
    try:
        student_profile = StudentProfile(**profile_data)
        profile_dict = student_profile.model_dump()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid student profile data: {str(e)}"
        )
    
    # 6. file_type에 따라 학생 정보 저장 또는 AI 함수 호출
    try:
        from ai_module import generate_goals, generate_weekly_plan, generate_weekly_materials
        
        if file_type == "student_info":
            generated_data = profile_dict
        elif file_type == "goal":
            generated_data = generate_goals(profile_dict)
        elif file_type == "weekly_content":
            generated_data = generate_weekly_plan(profile_dict)
        elif file_type == "weekly_material":
            generated_data = generate_weekly_materials(profile_dict)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI module error: {str(e)}"
        )
    
    # 7. 디스크에 파일 저장
    try:
        file_path = save_json_file(
            str(iep_version_uuid),
            file_type,
            generated_data
        )
    except FileStorageError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # 8. DB에 메타데이터 저장
    try:
        iep_file = IEPFile(
            iep_version_id=iep_version_uuid,
            file_type=file_type,
            file_path=file_path
        )
        
        db.add(iep_file)
        db.commit()
        db.refresh(iep_file)
        
        return iep_file
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.put("/{file_id}", response_model=IEPFileResponse)
async def update_iep_file(
    file_id: UUID,
    file: UploadFile = File(..., description="업데이트할 JSON 파일"),
    db: Session = Depends(get_db),
) -> IEPFileResponse:
    """
    IEP 파일 업데이트
    
    기존 JSON 파일을 덮어쓰기합니다.
    - 새 파일을 타임스탬프와 함께 저장
    - IEPFile 레코드의 file_path 갱신
    - updated_at 자동 갱신
    
    **프로세스:**
    1. 기존 IEP 파일 레코드 조회
    2. 업로드된 파일 검증 (JSON 형식)
    3. 새 파일을 디스크에 저장 (새 타임스탬프)
    4. DB의 file_path와 updated_at 갱신
    
    **요청 (multipart/form-data):**
    - **file**: 업데이트할 JSON 파일 (.json)
    
    **응답:**
    - 업데이트된 IEP 파일 메타데이터
    
    **에러 응답:**
    - 400: JSON 파일 형식 오류
    - 404: IEP file not found
    - 500: 파일 저장 실패
    """
    # 1. 기존 파일 레코드 조회
    iep_file = db.query(IEPFile).filter(IEPFile.id == file_id).first()
    
    if not iep_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="IEP file not found"
        )
    
    # 2. 업로드된 파일 읽기 및 JSON 검증
    try:
        content = await file.read()
        json_data = json.loads(content.decode('utf-8'))
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
    
    # 3. 새 파일 저장 (타임스탬프 변경으로 새 파일명)
    try:
        new_file_path = save_json_file(
            str(iep_file.iep_version_id),
            iep_file.file_type,
            json_data
        )
    except FileStorageError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # 4. DB 업데이트
    try:
        iep_file.file_path = new_file_path
        iep_file.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(iep_file)
        
        return iep_file
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update database: {str(e)}"
        )
