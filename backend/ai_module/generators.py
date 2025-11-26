"""
AI 모듈: IEP 컨텐츠 생성 함수들 (Placeholder)

실제 AI 로직은 별도로 구현됩니다.
현재는 입력된 도메인을 기반으로 Mock 데이터를 반환합니다.

Functions:
    - generate_goals: 연간/학기 목표 생성
    - generate_weekly_plan: 주차별 학습 내용 생성 (20주)
    - generate_weekly_materials: 주차별 학습 자료 생성 (20주)
"""

from __future__ import annotations

from typing import Any


def generate_goals(student_profile: dict[str, Any]) -> dict:
    """
    학생 프로필을 기반으로 연간/학기 목표 생성 (Placeholder)
    
    Args:
        student_profile: 학생 프로필 딕셔너리 (20개 필드)
            - name (str): 학생 이름
            - birth (str): 생년월일 (YYYY-MM-DD)
            - grade (int): 학년 (1-12)
            - current_semester (int): 현재 학기 (1 or 2)
            - start_date (str): 학기 시작일 (YYYY-MM-DD)
            - end_date (str): 학기 종료일 (YYYY-MM-DD)
            - guardian_opinion (str): 보호자 의견
            - cognitive_level (str): 인지 수준
            - social_psych_level (str): 사회심리 수준
            - motor_daily_level (str): 운동 일상생활 수준
            - vci_score (int): 언어이해지표
            - visual_spatial_score (int): 시공간지표
            - fri_score (int): 유동추론지표
            - wmi_score (int): 작업기억지표
            - psi_score (int): 처리속도지표
            - fsiq_score (int): 전체 IQ
            - korean_performance_level (str): 국어 수행 수준
            - math_performance_level (str): 수학 수행 수준
            - korean_domain (list[str]): 국어 도메인 선택
            - math_domain (list[str]): 수학 도메인 선택
    
    Returns:
        dict: 연간/학기 목표 (선택된 도메인만)
            - annual_{domain}_goal: 연간 목표
            - semester_{domain}_goal: 학기 목표
    
    Note:
        실제 AI 로직으로 대체 필요
        현재는 Mock 데이터 반환
    """
    # 안전하게 도메인 선택 필드 가져오기
    korean_domains = student_profile.get("korean_domain", [])
    math_domains = student_profile.get("math_domain", [])
    
    # 학생 정보 (Mock 데이터 생성용)
    student_name = student_profile.get("name", "학생")
    grade = student_profile.get("grade", 1)
    start_date = student_profile.get("start_date", "")
    end_date = student_profile.get("end_date", "")
    
    goals = {}
    
    # 국어 도메인별 목표
    for domain in korean_domains:
        domain_key = _get_domain_key(domain)
        goals[f"annual_{domain_key}_goal"] = (
            f"[연간 목표 - 국어/{domain}] {student_name} 학생의 {domain} 능력 향상 (Mock)"
        )
        goals[f"semester_{domain_key}_goal"] = (
            f"[학기 목표 - 국어/{domain}] {grade}학년 {domain} 핵심 개념 습득 "
            f"({start_date} ~ {end_date}) (Mock)"
        )
    
    # 수학 도메인별 목표
    for domain in math_domains:
        domain_key = _get_domain_key(domain)
        goals[f"annual_{domain_key}_goal"] = (
            f"[연간 목표 - 수학/{domain}] {student_name} 학생의 {domain} 능력 향상 (Mock)"
        )
        goals[f"semester_{domain_key}_goal"] = (
            f"[학기 목표 - 수학/{domain}] {grade}학년 {domain} 핵심 개념 습득 "
            f"({start_date} ~ {end_date}) (Mock)"
        )
    
    return goals


def generate_weekly_plan(student_profile: dict[str, Any]) -> dict:
    """
    학생 프로필을 기반으로 주차별 학습 내용 생성 (Placeholder)
    
    Args:
        student_profile: 학생 프로필 딕셔너리 (20개 필드)
    
    Returns:
        dict: 주차별 학습 내용 (20주, 선택된 도메인만)
            - {domain}_weeklyContent: 20개 요소 배열
    
    Note:
        실제 AI 로직으로 대체 필요
        현재는 Mock 데이터 반환
    """
    # 안전하게 도메인 선택 필드 가져오기
    korean_domains = student_profile.get("korean_domain", [])
    math_domains = student_profile.get("math_domain", [])
    
    weekly_plan = {}
    
    all_domains = korean_domains + math_domains
    for domain in all_domains:
        domain_key = _get_domain_key(domain)
        weekly_plan[f"{domain_key}_weeklyContent"] = [
            f"[{domain}] {week}주차 학습 내용 (Mock)"
            for week in range(1, 21)
        ]
    
    return weekly_plan


def generate_weekly_materials(student_profile: dict[str, Any]) -> dict:
    """
    학생 프로필을 기반으로 주차별 학습 자료 생성 (Placeholder)
    
    Args:
        student_profile: 학생 프로필 딕셔너리 (20개 필드)
    
    Returns:
        dict: 주차별 학습 자료 (20주, 선택된 도메인만)
            - {domain}_weekly_material: 20개 주차별 자료 배열
    
    Note:
        실제 AI 로직으로 대체 필요
        현재는 Mock 데이터 반환
    """
    # 안전하게 도메인 선택 필드 가져오기
    korean_domains = student_profile.get("korean_domain", [])
    math_domains = student_profile.get("math_domain", [])
    
    weekly_materials = {}
    
    all_domains = korean_domains + math_domains
    for domain in all_domains:
        domain_key = _get_domain_key(domain)
        weekly_materials[f"{domain_key}_weekly_material"] = [
            {
                "week": week,
                "materials": [
                    {
                        "title": f"{domain} {week}주차 학습자료 예시 (Mock)",
                        "file_type": "PDF",
                        "url": f"https://example.com/edunet/{domain_key}/week{week}/material1.pdf"
                    }
                ]
            }
            for week in range(1, 21)
        ]
    
    return weekly_materials


def _get_domain_key(domain: str) -> str:
    """
    도메인 이름을 키로 변환
    
    Args:
        domain: 도메인 이름 (한글 또는 영문)
    
    Returns:
        str: 도메인 키 (camelCase)
    """
    # 한글 → 영문 매핑
    domain_mapping = {
        "듣기말하기": "listeningSpeaking",
        "읽기": "reading",
        "쓰기": "writing",
        "문법": "grammar",
        "문학": "literature",
        "매체": "mediaLiteracy",
        "수와 연산": "numbersOperations",
        "변화와 관계": "changeAndRelations",
        "도형과 측정": "geometryMeasurement",
        "자료와 가능성": "dataAndProbability",
    }
    
    # 이미 영문 키인 경우 그대로 반환
    return domain_mapping.get(domain, domain)


__all__ = ["generate_goals", "generate_weekly_plan", "generate_weekly_materials"]

