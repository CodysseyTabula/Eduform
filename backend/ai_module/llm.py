"""
LLM 기반 IEP 컨텐츠 생성기

환경 변수:
- OPENAI_API_KEY: 설정되면 OpenAI 호출을 시도
- AI_MODE=llm 일 때 API에서 이 모듈을 사용하도록 선택
"""
from __future__ import annotations

import os
import json
from typing import Any, Dict, List

from openai import OpenAI


# ==================== 공용 유틸 ====================

def _get_openai_client() -> OpenAI | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    return OpenAI(api_key=api_key)


def _safe_chat_json(client: OpenAI, prompt: str) -> Dict[str, Any]:
    """LLM 호출 (실패 시 빈 dict 반환)"""
    try:
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        content = response.choices[0].message.content
        return json.loads(content) if content else {}
    except Exception:
        return {}


# ==================== Goals ====================

def generate_goals_llm(student_profile: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    """
    학생 프로필을 기반으로 연간/학기 목표 생성.
    - OPENAI_API_KEY가 있으면 LLM 호출
    - 없거나 실패 시 간단한 템플릿으로 생성 (Mock 문구 제거)
    """
    client = _get_openai_client()
    domains: List[str] = student_profile.get("korean_domain", []) + student_profile.get("math_domain", [])
    if client:
        prompt = (
            "학생 프로필 기반 IEP 목표를 JSON으로 생성하세요. "
            "응답 키는 도메인 영문 키(listeningSpeaking, reading, writing, grammar, literature, mediaLiteracy, "
            "numbersOperations, changeAndRelations, geometryMeasurement, dataAndProbability)이며, "
            "각 값은 {\"annual_goal\": str, \"semester_goal\": str} 형태로 출력하세요. "
            f"학생 정보: {json.dumps(student_profile, ensure_ascii=False)} "
            f"대상 도메인: {domains}"
        )
        result = _safe_chat_json(client, prompt)
        if result:
            return result

    # Fallback 템플릿 (Mock 문구 제거)
    name = student_profile.get("name", "학생")
    grade = student_profile.get("grade", "")
    start = student_profile.get("start_date", "")
    end = student_profile.get("end_date", "")
    goals: Dict[str, Dict[str, str]] = {}
    for domain in domains:
        goals[domain] = {
            "annual_goal": f"{name}의 {domain} 역량을 학년 수준에 맞춰 향상시킨다.",
            "semester_goal": f"{grade}학년 {domain} 핵심 개념을 {start}~{end} 기간 동안 습득한다.",
        }
    return goals


# ==================== Weekly Plan ====================

def generate_weekly_plan_llm(student_profile: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """
    주차별 학습 내용 생성 (20주).
    - OPENAI_API_KEY가 있으면 LLM 호출
    - 없거나 실패 시 템플릿 생성
    """
    client = _get_openai_client()
    domains: List[str] = student_profile.get("korean_domain", []) + student_profile.get("math_domain", [])
    if client:
        prompt = (
            "학생 프로필 기반 20주 학습 계획을 JSON으로 생성하세요. "
            "응답 키는 도메인 영문 키, 각 값은 [{\"week\": int, \"content\": str}, ...] (20주) 형식입니다. "
            f"학생 정보: {json.dumps(student_profile, ensure_ascii=False)} "
            f"대상 도메인: {domains}"
        )
        result = _safe_chat_json(client, prompt)
        if result:
            return result

    # Fallback 템플릿
    plan: Dict[str, List[Dict[str, Any]]] = {}
    for domain in domains:
        plan[domain] = [{"week": w, "content": f"{domain} 영역 {w}주차 학습 목표를 달성한다."} for w in range(1, 21)]
    return plan


# ==================== Weekly Materials ====================

def generate_weekly_materials_llm(student_profile: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """
    주차별 학습 자료 생성 (20주).
    - OPENAI_API_KEY가 있으면 LLM 호출
    - 없거나 실패 시 템플릿 생성
    """
    client = _get_openai_client()
    domains: List[str] = student_profile.get("korean_domain", []) + student_profile.get("math_domain", [])
    if client:
        prompt = (
            "학생 프로필 기반 20주 학습 자료 추천을 JSON으로 생성하세요. "
            "응답 키는 도메인 영문 키, 각 값은 [{\"week\": int, \"material_url\": str}, ...] (20주) 형식입니다. "
            f"학생 정보: {json.dumps(student_profile, ensure_ascii=False)} "
            f"대상 도메인: {domains}"
        )
        result = _safe_chat_json(client, prompt)
        if result:
            return result

    # Fallback 템플릿
    materials: Dict[str, List[Dict[str, Any]]] = {}
    for domain in domains:
        materials[domain] = [
            {"week": w, "material_url": f"https://example.com/{domain}/week{w}"} for w in range(1, 21)
        ]
    return materials


__all__ = [
    "generate_goals_llm",
    "generate_weekly_plan_llm",
    "generate_weekly_materials_llm",
]
