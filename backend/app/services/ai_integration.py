"""
AI 통합 서비스 레이어

AI 모듈의 3개 함수를 순차 호출하여 IEP 파일을 생성하고 디스크/DB에 저장합니다.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from ai_module import generate_goals, generate_weekly_plan, generate_weekly_materials
from app.models.iep_file import IEPFile
from app.services.file_storage import save_json_file, FileStorageError


class AIIntegrationError(Exception):
    """AI 통합 관련 예외"""
    pass


def create_iep_files_with_ai(
    iep_version_id: UUID,
    student_profile: dict[str, Any],
    db: Session
) -> list[IEPFile]:
    """
    AI 모듈의 3개 함수를 호출하여 IEP 파일 생성 및 저장
    
    프로세스:
    1. AI 모듈 호출 (3개 함수 순차 호출):
       - generate_goals(student_profile) → goals.json
       - generate_weekly_plan(student_profile) → weekly_plan.json
       - generate_weekly_materials(student_profile) → weekly_materials.json
    2. 디스크 저장: 3개 JSON 파일 저장
    3. DB 저장: 3개 IEPFile 메타데이터 레코드 생성
    
    Args:
        iep_version_id: IEP 버전 UUID
        student_profile: 학생 프로필 딕셔너리 (20개 필드)
            - name, birth, grade, current_semester
            - start_date, end_date (학기 기간)
            - guardian_opinion, cognitive_level, social_psych_level, motor_daily_level
            - vci_score, visual_spatial_score, fri_score, wmi_score, psi_score, fsiq_score
            - korean_performance_level, math_performance_level
            - korean_domain (list), math_domain (list)
        db: 데이터베이스 세션
    
    Returns:
        list[IEPFile]: 생성된 3개 IEP 파일 메타데이터 목록
    
    Raises:
        AIIntegrationError: AI 모듈 호출 또는 파일 저장 실패 시
    
    Note:
        트랜잭션 처리: 예외 발생 시 rollback 수행
    """
    try:
        # 1. AI 모듈 호출: 3개 함수 순차 호출
        goals = generate_goals(student_profile)
        weekly_plan = generate_weekly_plan(student_profile)
        weekly_materials = generate_weekly_materials(student_profile)
        
    except Exception as e:
        raise AIIntegrationError(f"AI 모듈 호출 실패: {e}") from e
    
    # 파일 경로 저장용 딕셔너리
    file_paths: dict[str, str] = {}
    
    try:
        # 2. 디스크에 3개 JSON 파일 저장
        file_paths["goals"] = save_json_file(
            str(iep_version_id),
            "goals",
            goals
        )
        
        file_paths["weekly_plan"] = save_json_file(
            str(iep_version_id),
            "weekly_plan",
            weekly_plan
        )
        
        file_paths["weekly_materials"] = save_json_file(
            str(iep_version_id),
            "weekly_materials",
            weekly_materials
        )
        
    except FileStorageError as e:
        raise AIIntegrationError(f"파일 저장 실패: {e}") from e
    
    try:
        # 3. DB에 메타데이터 저장 (3개 레코드)
        goals_file = IEPFile(
            iep_version_id=iep_version_id,
            file_type="goals",
            file_path=file_paths["goals"]
        )
        
        plan_file = IEPFile(
            iep_version_id=iep_version_id,
            file_type="weekly_plan",
            file_path=file_paths["weekly_plan"]
        )
        
        materials_file = IEPFile(
            iep_version_id=iep_version_id,
            file_type="weekly_materials",
            file_path=file_paths["weekly_materials"]
        )
        
        # DB에 추가 및 커밋
        db.add_all([goals_file, plan_file, materials_file])
        db.commit()
        
        # 최신 상태 반영
        db.refresh(goals_file)
        db.refresh(plan_file)
        db.refresh(materials_file)
        
        file_records = [goals_file, plan_file, materials_file]
        
        return file_records
    
    except Exception as e:
        # DB 작업 실패 시 rollback
        db.rollback()
        raise AIIntegrationError(f"DB 메타데이터 저장 실패: {e}") from e


__all__ = ["create_iep_files_with_ai", "AIIntegrationError"]


