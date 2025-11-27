#!/usr/bin/env python3
"""
AI 모듈 간단 테스트 스크립트

ai_module의 함수들이 제대로 작동하는지 테스트합니다.
"""

import sys
import os
from pathlib import Path

# 부모 디렉토리(backend)를 경로에 추가
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from ai_module.generators import (
    generate_goals,
    generate_weekly_plan,
    generate_weekly_materials
)


def test_generators():
    """generators.py의 함수들 테스트"""
    
    # 샘플 학생 프로필
    sample_profile = {
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
    
    print("=" * 60)
    print("AI 모듈 테스트 시작")
    print("=" * 60)
    
    # 1. generate_goals 테스트
    print("\n[1] generate_goals 테스트...")
    try:
        goals = generate_goals(sample_profile)
        print(f"✓ 성공: {len(goals)}개 도메인의 목표 생성됨")
        
        for domain_key, goal_data in goals.items():
            print(f"  - {domain_key}:")
            print(f"    연간 목표: {goal_data['annual_goal'][:50]}...")
            print(f"    학기 목표: {goal_data['semester_goal'][:50]}...")
        
        # 검증
        assert isinstance(goals, dict), "결과가 딕셔너리가 아님"
        assert "reading" in goals, "읽기 도메인이 없음"
        assert "writing" in goals, "쓰기 도메인이 없음"
        assert "numbersOperations" in goals, "수와 연산 도메인이 없음"
        
        for domain_key, goal_data in goals.items():
            assert "annual_goal" in goal_data, f"{domain_key}에 annual_goal이 없음"
            assert "semester_goal" in goal_data, f"{domain_key}에 semester_goal이 없음"
            assert len(goal_data["annual_goal"]) > 0, f"{domain_key}의 annual_goal이 비어있음"
            assert len(goal_data["semester_goal"]) > 0, f"{domain_key}의 semester_goal이 비어있음"
        
        print("  ✓ 모든 검증 통과")
        
    except Exception as e:
        print(f"✗ 실패: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 2. generate_weekly_plan 테스트
    print("\n[2] generate_weekly_plan 테스트...")
    try:
        weekly_plan = generate_weekly_plan(sample_profile)
        print(f"✓ 성공: {len(weekly_plan)}개 도메인의 주차별 계획 생성됨")
        
        for domain_key, weekly_list in weekly_plan.items():
            print(f"  - {domain_key}: {len(weekly_list)}주차")
            if weekly_list:
                print(f"    예시 (1주차): {weekly_list[0]['content'][:50]}...")
        
        # 검증
        assert isinstance(weekly_plan, dict), "결과가 딕셔너리가 아님"
        assert "reading" in weekly_plan, "읽기 도메인이 없음"
        assert "writing" in weekly_plan, "쓰기 도메인이 없음"
        assert "numbersOperations" in weekly_plan, "수와 연산 도메인이 없음"
        
        for domain_key, weekly_list in weekly_plan.items():
            assert isinstance(weekly_list, list), f"{domain_key}의 결과가 리스트가 아님"
            assert len(weekly_list) == 20, f"{domain_key}가 20주차가 아님 (실제: {len(weekly_list)}주차)"
            
            for week_data in weekly_list:
                assert "week" in week_data, "week 필드가 없음"
                assert "content" in week_data, "content 필드가 없음"
                assert 1 <= week_data["week"] <= 20, f"주차 번호가 범위를 벗어남: {week_data['week']}"
        
        print("  ✓ 모든 검증 통과")
        
    except Exception as e:
        print(f"✗ 실패: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 3. generate_weekly_materials 테스트
    print("\n[3] generate_weekly_materials 테스트...")
    try:
        weekly_materials = generate_weekly_materials(sample_profile)
        print(f"✓ 성공: {len(weekly_materials)}개 도메인의 주차별 자료 생성됨")
        
        for domain_key, materials_list in weekly_materials.items():
            print(f"  - {domain_key}: {len(materials_list)}주차")
            if materials_list:
                print(f"    예시 (1주차): {materials_list[0]['material_url']}")
        
        # 검증
        assert isinstance(weekly_materials, dict), "결과가 딕셔너리가 아님"
        assert "reading" in weekly_materials, "읽기 도메인이 없음"
        assert "writing" in weekly_materials, "쓰기 도메인이 없음"
        assert "numbersOperations" in weekly_materials, "수와 연산 도메인이 없음"
        
        for domain_key, materials_list in weekly_materials.items():
            assert isinstance(materials_list, list), f"{domain_key}의 결과가 리스트가 아님"
            assert len(materials_list) == 20, f"{domain_key}가 20주차가 아님 (실제: {len(materials_list)}주차)"
            
            for week_data in materials_list:
                assert "week" in week_data, "week 필드가 없음"
                assert "material_url" in week_data, "material_url 필드가 없음"
                assert 1 <= week_data["week"] <= 20, f"주차 번호가 범위를 벗어남: {week_data['week']}"
        
        print("  ✓ 모든 검증 통과")
        
    except Exception as e:
        print(f"✗ 실패: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 4. 빈 도메인 테스트
    print("\n[4] 빈 도메인 테스트...")
    try:
        empty_profile = {
            "name": "테스트",
            "grade": 1,
            "korean_domain": [],
            "math_domain": []
        }
        
        empty_goals = generate_goals(empty_profile)
        assert isinstance(empty_goals, dict), "결과가 딕셔너리가 아님"
        assert len(empty_goals) == 0, "빈 도메인인데 결과가 있음"
        
        print("  ✓ 빈 도메인 처리 정상")
        
    except Exception as e:
        print(f"✗ 실패: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("모든 테스트 통과! ✓")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_generators()
    sys.exit(0 if success else 1)

