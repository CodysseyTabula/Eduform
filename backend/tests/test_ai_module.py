"""
AI 모듈 테스트

ai_module의 함수들이 제대로 작동하는지 테스트합니다.
"""

import pytest
from ai_module.generators import (
    generate_goals,
    generate_weekly_plan,
    generate_weekly_materials
)


@pytest.fixture
def sample_student_profile():
    """테스트용 샘플 학생 프로필"""
    return {
        "name": "홍길동",
        "birth": "2010-05-15",
        "grade": 3,
        "current_semester": 1,
        "start_date": "2024-03-01",
        "end_date": "2024-08-31",
        "guardian_opinion": "학습에 적극적인 자세를 보이고 있습니다.",
        "cognitive_level": "보통",
        "social_psych_level": "양호",
        "motor_daily_level": "양호",
        "vci_score": 95,
        "visual_spatial_score": 88,
        "fri_score": 92,
        "wmi_score": 90,
        "psi_score": 85,
        "fsiq_score": 90,
        "korean_performance_level": "보통",
        "math_performance_level": "보통",
        "korean_domain": ["읽기", "쓰기"],
        "math_domain": ["수와 연산"]
    }


def test_generate_goals_basic(sample_student_profile):
    """generate_goals 기본 동작 테스트"""
    result = generate_goals(sample_student_profile)
    
    # 결과가 딕셔너리인지 확인
    assert isinstance(result, dict)
    
    # 선택된 도메인만 포함되어야 함
    assert "reading" in result
    assert "writing" in result
    assert "numbersOperations" in result
    
    # 각 도메인에 annual_goal과 semester_goal이 있는지 확인
    for domain_key, goals in result.items():
        assert "annual_goal" in goals
        assert "semester_goal" in goals
        assert isinstance(goals["annual_goal"], str)
        assert isinstance(goals["semester_goal"], str)
        assert len(goals["annual_goal"]) > 0
        assert len(goals["semester_goal"]) > 0


def test_generate_goals_empty_domains():
    """도메인이 선택되지 않은 경우 테스트"""
    profile = {
        "name": "테스트",
        "grade": 1,
        "korean_domain": [],
        "math_domain": []
    }
    
    result = generate_goals(profile)
    
    # 빈 딕셔너리 반환되어야 함
    assert isinstance(result, dict)
    assert len(result) == 0


def test_generate_weekly_plan_basic(sample_student_profile):
    """generate_weekly_plan 기본 동작 테스트"""
    result = generate_weekly_plan(sample_student_profile)
    
    # 결과가 딕셔너리인지 확인
    assert isinstance(result, dict)
    
    # 선택된 도메인만 포함되어야 함
    assert "reading" in result
    assert "writing" in result
    assert "numbersOperations" in result
    
    # 각 도메인에 20주차 데이터가 있는지 확인
    for domain_key, weekly_list in result.items():
        assert isinstance(weekly_list, list)
        assert len(weekly_list) == 20
        
        # 각 주차 데이터 확인
        for week_data in weekly_list:
            assert "week" in week_data
            assert "content" in week_data
            assert isinstance(week_data["week"], int)
            assert 1 <= week_data["week"] <= 20
            assert isinstance(week_data["content"], str)
            assert len(week_data["content"]) > 0


def test_generate_weekly_materials_basic(sample_student_profile):
    """generate_weekly_materials 기본 동작 테스트"""
    result = generate_weekly_materials(sample_student_profile)
    
    # 결과가 딕셔너리인지 확인
    assert isinstance(result, dict)
    
    # 선택된 도메인만 포함되어야 함
    assert "reading" in result
    assert "writing" in result
    assert "numbersOperations" in result
    
    # 각 도메인에 20주차 데이터가 있는지 확인
    for domain_key, weekly_list in result.items():
        assert isinstance(weekly_list, list)
        assert len(weekly_list) == 20
        
        # 각 주차 데이터 확인
        for week_data in weekly_list:
            assert "week" in week_data
            assert "material_url" in week_data
            assert isinstance(week_data["week"], int)
            assert 1 <= week_data["week"] <= 20
            assert isinstance(week_data["material_url"], str)
            assert len(week_data["material_url"]) > 0


def test_generate_goals_korean_domain_names():
    """한글 도메인명 처리 테스트"""
    profile = {
        "name": "테스트",
        "grade": 1,
        "korean_domain": ["듣기말하기", "읽기"],
        "math_domain": []
    }
    
    result = generate_goals(profile)
    
    # 영문 키로 변환되어야 함
    assert "listeningSpeaking" in result
    assert "reading" in result


def test_generate_goals_math_domain_names():
    """수학 도메인명 처리 테스트"""
    profile = {
        "name": "테스트",
        "grade": 1,
        "korean_domain": [],
        "math_domain": ["수와 연산", "도형과 측정"]
    }
    
    result = generate_goals(profile)
    
    # 영문 키로 변환되어야 함
    assert "numbersOperations" in result
    assert "geometryMeasurement" in result


def test_generate_goals_mixed_domains():
    """국어와 수학 도메인 혼합 테스트"""
    profile = {
        "name": "테스트",
        "grade": 1,
        "korean_domain": ["읽기"],
        "math_domain": ["수와 연산"]
    }
    
    result = generate_goals(profile)
    
    assert "reading" in result
    assert "numbersOperations" in result
    assert len(result) == 2


