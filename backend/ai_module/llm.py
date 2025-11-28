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
from pydantic import BaseModel


# ==================== 공용 유틸 ====================

def _get_openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY가 설정되지 않았습니다. OpenAI API를 사용하려면 OPENAI_API_KEY 환경 변수를 설정해주세요.")
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
    - OPENAI_API_KEY가 필수입니다.
    """
    client = _get_openai_client()
    domains: List[str] = student_profile.get("korean_domain", []) + student_profile.get("math_domain", [])
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
    
    # 실패 시 에러 발생
    raise RuntimeError("LLM 호출이 실패했습니다. OpenAI API 키를 확인해주세요.")


# ==================== Weekly Plan ====================

class WeekContentItem(BaseModel):
    """단일 주차의 학습 내용"""
    week: int
    content: str


class DomainWeeklyContent(BaseModel):
    """단일 도메인의 주차별 학습 내용 (20주)"""
    listeningSpeaking: List[WeekContentItem] = []
    reading: List[WeekContentItem] = []
    writing: List[WeekContentItem] = []
    grammar: List[WeekContentItem] = []
    literature: List[WeekContentItem] = []
    mediaLiteracy: List[WeekContentItem] = []
    numbersOperations: List[WeekContentItem] = []
    changeAndRelations: List[WeekContentItem] = []
    geometryMeasurement: List[WeekContentItem] = []
    dataAndProbability: List[WeekContentItem] = []


def generate_weekly_plan_llm(student_profile: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """
    주차별 학습 내용 생성 (20주).
    - OPENAI_API_KEY가 필수입니다.
    - Structured output을 사용하여 정확한 형식 보장
    """
    client = _get_openai_client()
    domains: List[str] = student_profile.get("korean_domain", []) + student_profile.get("math_domain", [])
    prompt = (
        "학생 프로필 기반 주차별 학습 계획을 생성하세요.\n\n"
        "**매우 중요: 반드시 정확히 20개의 항목을 생성해야 합니다. 10개나 다른 개수가 아닌 정확히 20개입니다.**\n\n"
        "요구사항:\n"
        "- 각 도메인마다 정확히 20개의 항목이 필요합니다 (week 1부터 20까지)\n"
        "- 각 항목의 content는 구체적이고 실현 가능한 학습 내용이어야 합니다\n"
        "- 빈 문자열이나 공백만 있는 content는 절대 사용하지 마세요\n"
        "- 주차 번호(week)는 1부터 20까지 순서대로 1씩 증가해야 합니다\n\n"
        f"학생 정보: {json.dumps(student_profile, ensure_ascii=False)}\n"
        f"대상 도메인: {domains}\n\n"
        "**다시 한번 강조: 각 도메인마다 정확히 20개의 항목을 생성하세요. 10개가 아닌 20개입니다.**"
    )
    
    try:
        response = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[{"role": "user", "content": prompt}],
            response_format=DomainWeeklyContent,
            temperature=0.3,
        )
        
        result_parsed = response.choices[0].message.parsed
        
        # Pydantic 모델을 dict로 변환
        result_dict = {}
        domain_keys = [
            "listeningSpeaking", "reading", "writing", "grammar", "literature", "mediaLiteracy",
            "numbersOperations", "changeAndRelations", "geometryMeasurement", "dataAndProbability"
        ]
        target_domains = set(domains) if domains else set(domain_keys)
        
        for domain_key in domain_keys:
            # 선택된 도메인만 검증/생성 대상
            if domain_key not in target_domains:
                result_dict[domain_key] = []
                continue
            
            content_list = getattr(result_parsed, domain_key, [])
            if isinstance(content_list, list):
                # 검증 없이 변환만 수행 (길이 제약 제거)
                result_dict[domain_key] = [
                    {"week": item.week, "content": item.content}
                    for item in content_list
                    if isinstance(item, WeekContentItem)
                ]
            else:
                result_dict[domain_key] = []
        
        return result_dict
    
    except Exception as e:
        raise RuntimeError(f"LLM 호출이 실패했습니다: {str(e)}")


# ==================== Weekly Materials ====================

def generate_weekly_materials_llm(student_profile: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """
    주차별 학습 자료 생성 (20주).
    - OPENAI_API_KEY가 필수입니다.
    """
    client = _get_openai_client()
    domains: List[str] = student_profile.get("korean_domain", []) + student_profile.get("math_domain", [])
    prompt = (
        "학생 프로필 기반 20주 학습 자료 추천을 JSON으로 생성하세요. "
        "응답 키는 도메인 영문 키, 각 값은 [{\"week\": int, \"material_url\": str}, ...] (20주) 형식입니다. "
        f"학생 정보: {json.dumps(student_profile, ensure_ascii=False)} "
        f"대상 도메인: {domains}"
    )
    result = _safe_chat_json(client, prompt)
    if result:
        return result
    
    # 실패 시 에러 발생
    raise RuntimeError("LLM 호출이 실패했습니다. OpenAI API 키를 확인해주세요.")


__all__ = [
    "generate_goals_llm",
    "generate_weekly_plan_llm",
    "generate_weekly_materials_llm",
]
