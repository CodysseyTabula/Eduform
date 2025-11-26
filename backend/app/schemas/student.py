from __future__ import annotations

from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class StudentCreate(BaseModel):
    """학생 생성 요청 스키마"""
    
    name: str = Field(..., min_length=1, max_length=100, description="학생 이름")
    birth: date = Field(..., description="생년월일 (YYYY-MM-DD)")


class StudentResponse(BaseModel):
    """학생 응답 스키마"""
    
    id: UUID
    name: str
    birth: date

    model_config = ConfigDict(from_attributes=True)
