"""
학생 프로필 스키마 - IEP 파일 생성 요청에 사용
"""
from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class StudentProfile(BaseModel):
    """
    IEP 파일 생성을 위한 학생 프로필 스키마 (20개 필드)
    
    AI 모듈에 전달되는 학생 정보를 정의합니다.
    """
    # 기본 정보
    name: str = Field(..., min_length=1, max_length=100, description="학생 이름")
    birth: str = Field(..., description="생년월일 (YYYY-MM-DD)")
    grade: int = Field(..., ge=1, le=12, description="학년 (1-12)")
    current_semester: int = Field(..., ge=1, le=2, description="현재 학기 (1 or 2)")
    
    # 학기 기간
    start_date: str = Field(..., description="학기 시작일 (YYYY-MM-DD)")
    end_date: str = Field(..., description="학기 종료일 (YYYY-MM-DD)")
    
    # 수준 평가
    guardian_opinion: str = Field(..., description="보호자 의견")
    cognitive_level: str = Field(..., description="인지 수준")
    social_psych_level: str = Field(..., description="사회심리 수준")
    motor_daily_level: str = Field(..., description="운동 일상생활 수준")
    
    # K-WISC-V 검사 결과 (6개 지표)
    vci_score: int = Field(..., ge=0, le=200, description="언어이해지표 (VCI)")
    visual_spatial_score: int = Field(..., ge=0, le=200, description="시공간지표 (VSI)")
    fri_score: int = Field(..., ge=0, le=200, description="유동추론지표 (FRI)")
    wmi_score: int = Field(..., ge=0, le=200, description="작업기억지표 (WMI)")
    psi_score: int = Field(..., ge=0, le=200, description="처리속도지표 (PSI)")
    fsiq_score: int = Field(..., ge=0, le=200, description="전체 IQ (FSIQ)")
    
    # 교과 수행 수준
    korean_performance_level: str = Field(..., description="국어 수행 수준")
    math_performance_level: str = Field(..., description="수학 수행 수준")
    
    # 도메인 선택 (영문 camelCase 형식)
    korean_domain: List[str] = Field(
        ...,
        description="국어 도메인 선택 (listeningSpeaking, reading, writing, grammar, literature, mediaLiteracy)"
    )
    math_domain: List[str] = Field(
        ...,
        description="수학 도메인 선택 (numbersOperations, changeAndRelations, geometryMeasurement, dataAndProbability)"
    )


__all__ = ["StudentProfile"]



