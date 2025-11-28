from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional, Dict, Any, List
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.student_profile import StudentProfile


class IEPFileCreateRequest(BaseModel):
    """IEP 파일 생성 요청 스키마"""
    
    iep_version_id: UUID = Field(..., description="IEP 버전 ID")
    student_profile: StudentProfile = Field(..., description="학생 프로필 (20개 필드)")


class IEPFileResponse(BaseModel):
    """IEP 파일 메타데이터 응답 스키마"""
    
    id: UUID
    iep_version_id: UUID
    file_type: Literal["student_info", "goal", "weekly_content", "weekly_material"]
    file_path: str
    file_content: Dict[str, Any] | None = None
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Task 3.5: Goals JSON 스키마
# ============================================================================

class GoalsContent(BaseModel):
    """
    Goals JSON 구조 (스펙에 맞는 형식)
    
    실제 저장 형식: {annual_{domain}_goal: str, semester_{domain}_goal: str}
    선택된 도메인만 포함됨 (korean_domain, math_domain 배열에 따라 결정)
    
    국어 도메인: listeningSpeaking, reading, writing, grammar, literature, mediaLiteracy
    수학 도메인: numbersOperations, changeAndRelations, geometryMeasurement, dataAndProbability
    """
    file_type: Literal["goal"] = "goal"
    
    # 국어 도메인 (선택적 - 선택된 도메인만 포함)
    annual_listeningSpeaking_goal: Optional[str] = None
    semester_listeningSpeaking_goal: Optional[str] = None
    annual_reading_goal: Optional[str] = None
    semester_reading_goal: Optional[str] = None
    annual_writing_goal: Optional[str] = None
    semester_writing_goal: Optional[str] = None
    annual_grammar_goal: Optional[str] = None
    semester_grammar_goal: Optional[str] = None
    annual_literature_goal: Optional[str] = None
    semester_literature_goal: Optional[str] = None
    annual_mediaLiteracy_goal: Optional[str] = None
    semester_mediaLiteracy_goal: Optional[str] = None
    
    # 수학 도메인 (선택적 - 선택된 도메인만 포함)
    annual_numbersOperations_goal: Optional[str] = None
    semester_numbersOperations_goal: Optional[str] = None
    annual_changeAndRelations_goal: Optional[str] = None
    semester_changeAndRelations_goal: Optional[str] = None
    annual_geometryMeasurement_goal: Optional[str] = None
    semester_geometryMeasurement_goal: Optional[str] = None
    annual_dataAndProbability_goal: Optional[str] = None
    semester_dataAndProbability_goal: Optional[str] = None


# ============================================================================
# Task 3.6: Weekly Plan JSON 스키마
# ============================================================================

class WeeklyPlanContent(BaseModel):
    """
    Weekly Plan JSON 구조 (스펙에 맞는 형식)
    
    실제 저장 형식: {domain}_weeklyContent: [string (20개)]
    선택된 도메인만 포함됨 (korean_domain, math_domain 배열에 따라 결정)
    각 배열은 정확히 20개의 문자열을 포함 (1주차부터 20주차까지)
    """
    file_type: Literal["weekly"] = "weekly"
    
    # 국어 도메인 (선택적 - 선택된 도메인만 포함, 각 20개 문자열 배열)
    listeningSpeaking_weeklyContent: Optional[List[str]] = None
    reading_weeklyContent: Optional[List[str]] = None
    writing_weeklyContent: Optional[List[str]] = None
    grammar_weeklyContent: Optional[List[str]] = None
    literature_weeklyContent: Optional[List[str]] = None
    mediaLiteracy_weeklyContent: Optional[List[str]] = None
    
    # 수학 도메인 (선택적 - 선택된 도메인만 포함, 각 20개 문자열 배열)
    numbersOperations_weeklyContent: Optional[List[str]] = None
    changeAndRelations_weeklyContent: Optional[List[str]] = None
    geometryMeasurement_weeklyContent: Optional[List[str]] = None
    dataAndProbability_weeklyContent: Optional[List[str]] = None


# ============================================================================
# Task 3.7: Weekly Materials JSON 스키마
# ============================================================================

class MaterialItem(BaseModel):
    """학습 자료 항목 (에듀넷 자료)"""
    title: str = Field(..., description="자료 제목")
    url: str = Field(..., description="자료 URL")
    keywords: str = Field(default="", description="키워드")
    file_type: str = Field(default="", description="파일 타입")
    thumbnail_url: str = Field(default="", description="썸네일 이미지 URL")


class WeekMaterialItem(BaseModel):
    """주차별 학습 자료 항목"""
    week: int = Field(..., ge=1, le=20, description="주차 (1-20)")
    materials: List[MaterialItem] = Field(..., description="해당 주차의 학습 자료 리스트")


class WeeklyMaterialsContent(BaseModel):
    """
    Weekly Materials JSON 구조 (스펙에 맞는 형식)
    
    실제 저장 형식: {domain}_weekly_material: [{week: number, materials: [{title, url, keywords, file_type}]}]
    선택된 도메인만 포함됨 (korean_domain, math_domain 배열에 따라 결정)
    각 도메인은 20개의 WeekMaterialItem을 포함 (1주차부터 20주차까지)
    """
    file_type: Literal["material"] = "material"
    
    # 국어 도메인 (선택적 - 선택된 도메인만 포함, 각 20개 WeekMaterialItem 배열)
    listeningSpeaking_weekly_material: Optional[List[WeekMaterialItem]] = None
    reading_weekly_material: Optional[List[WeekMaterialItem]] = None
    writing_weekly_material: Optional[List[WeekMaterialItem]] = None
    grammar_weekly_material: Optional[List[WeekMaterialItem]] = None
    literature_weekly_material: Optional[List[WeekMaterialItem]] = None
    mediaLiteracy_weekly_material: Optional[List[WeekMaterialItem]] = None
    
    # 수학 도메인 (선택적 - 선택된 도메인만 포함, 각 20개 WeekMaterialItem 배열)
    numbersOperations_weekly_material: Optional[List[WeekMaterialItem]] = None
    changeAndRelations_weekly_material: Optional[List[WeekMaterialItem]] = None
    geometryMeasurement_weekly_material: Optional[List[WeekMaterialItem]] = None
    dataAndProbability_weekly_material: Optional[List[WeekMaterialItem]] = None
