"""
AI 모듈 - IEP 컨텐츠 생성

이 모듈은 학생 프로필(20개 필드)을 입력받아 3개의 IEP JSON 파일을 생성합니다.
실제 AI 로직은 별도 구현 예정이며, 현재는 placeholder 함수를 제공합니다.

Functions:
    - generate_goals: 연간/학기 목표 생성
    - generate_weekly_plan: 주차별 학습 내용 생성 (20주)
    - generate_weekly_materials: 주차별 학습 자료 생성 (20주)
"""

from .generators import generate_goals, generate_weekly_plan, generate_weekly_materials

__all__ = ["generate_goals", "generate_weekly_plan", "generate_weekly_materials"]



