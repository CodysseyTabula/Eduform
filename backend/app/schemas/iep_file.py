from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional, Dict, Any, List
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class IEPFileResponse(BaseModel):
    """IEP 파일 메타데이터 응답 스키마"""
    
    id: UUID
    iep_version_id: UUID
    file_type: Literal["goals", "weekly_plan", "weekly_materials"]
    file_path: str
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Task 3.5: Goals JSON 스키마
# ============================================================================

class GoalItem(BaseModel):
    """목표 항목 (연간 + 학기)"""
    annual_goal: str = Field(..., description="연간 목표")
    semester_goal: str = Field(..., description="학기 목표")


class GoalsContent(BaseModel):
    """
    Goals JSON 구조 (선택된 도메인만 포함)
    
    국어 도메인: listeningSpeaking, reading, writing, grammar, literature, mediaLiteracy
    수학 도메인: numbersOperations, changeAndRelations, geometryMeasurement, dataAndProbability
    """
    # 국어 도메인 (선택적)
    listeningSpeaking: Optional[GoalItem] = None
    reading: Optional[GoalItem] = None
    writing: Optional[GoalItem] = None
    grammar: Optional[GoalItem] = None
    literature: Optional[GoalItem] = None
    mediaLiteracy: Optional[GoalItem] = None
    
    # 수학 도메인 (선택적)
    numbersOperations: Optional[GoalItem] = None
    changeAndRelations: Optional[GoalItem] = None
    geometryMeasurement: Optional[GoalItem] = None
    dataAndProbability: Optional[GoalItem] = None


# ============================================================================
# Task 3.6: Weekly Plan JSON 스키마
# ============================================================================

class WeeklyContentItem(BaseModel):
    """주차별 학습 내용 항목"""
    week: int = Field(..., ge=1, le=20, description="주차 (1-20)")
    content: str = Field(..., description="주차별 학습 내용")


class WeeklyPlanContent(BaseModel):
    """
    Weekly Plan JSON 구조 (선택된 도메인만 포함, 각 도메인 20주)
    """
    # 국어 도메인 (선택적)
    listeningSpeaking: Optional[List[WeeklyContentItem]] = None
    reading: Optional[List[WeeklyContentItem]] = None
    writing: Optional[List[WeeklyContentItem]] = None
    grammar: Optional[List[WeeklyContentItem]] = None
    literature: Optional[List[WeeklyContentItem]] = None
    mediaLiteracy: Optional[List[WeeklyContentItem]] = None
    
    # 수학 도메인 (선택적)
    numbersOperations: Optional[List[WeeklyContentItem]] = None
    changeAndRelations: Optional[List[WeeklyContentItem]] = None
    geometryMeasurement: Optional[List[WeeklyContentItem]] = None
    dataAndProbability: Optional[List[WeeklyContentItem]] = None


# ============================================================================
# Task 3.7: Weekly Materials JSON 스키마
# ============================================================================

class WeeklyMaterialItem(BaseModel):
    """주차별 학습 자료 항목"""
    week: int = Field(..., ge=1, le=20, description="주차 (1-20)")
    material_url: str = Field(..., description="학습 자료 URL")


class WeeklyMaterialsContent(BaseModel):
    """
    Weekly Materials JSON 구조 (선택된 도메인만 포함, 각 도메인 20주)
    """
    # 국어 도메인 (선택적)
    listeningSpeaking: Optional[List[WeeklyMaterialItem]] = None
    reading: Optional[List[WeeklyMaterialItem]] = None
    writing: Optional[List[WeeklyMaterialItem]] = None
    grammar: Optional[List[WeeklyMaterialItem]] = None
    literature: Optional[List[WeeklyMaterialItem]] = None
    mediaLiteracy: Optional[List[WeeklyMaterialItem]] = None
    
    # 수학 도메인 (선택적)
    numbersOperations: Optional[List[WeeklyMaterialItem]] = None
    changeAndRelations: Optional[List[WeeklyMaterialItem]] = None
    geometryMeasurement: Optional[List[WeeklyMaterialItem]] = None
    dataAndProbability: Optional[List[WeeklyMaterialItem]] = None

