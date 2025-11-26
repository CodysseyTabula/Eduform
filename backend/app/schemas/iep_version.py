from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class IEPVersionCreate(BaseModel):
    """IEP 버전 생성 요청 스키마"""
    
    student_id: UUID = Field(..., description="학생 ID")
    year: str = Field(..., description="학년도 (예: '2024')")
    semester: str = Field(..., description="학기 (예: '1학기', '2학기')")
    grade: str = Field(..., description="학년 스냅샷 (예: '3', '4')")


class IEPVersionResponse(BaseModel):
    """IEP 버전 응답 스키마"""
    
    id: UUID
    student_id: UUID
    year: str
    semester: str
    grade: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

