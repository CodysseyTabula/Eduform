"""
Adapter helpers that wire the recommend_* modules into the API layer.

This module keeps the OpenAI interactions inside the three recommend_* files
while exposing simple helpers for goal and weekly content generation.
"""
from __future__ import annotations

import os
from typing import Any, Dict

import dotenv

from ai_module import recommend_goal
from ai_module import recommend_weekly

StudentProfileDict = Dict[str, Any]


_EN_TO_KR_KOREAN = {eng: kor for kor, eng in recommend_goal.KOREAN_DOMAIN_MAPPING.items()}
_EN_TO_KR_MATH = {eng: kor for kor, eng in recommend_goal.MATH_DOMAIN_MAPPING.items()}


def _to_korean_domain(domain: str, mapping: Dict[str, str]) -> str:
    """Convert an English domain key to its Korean label when possible."""
    return mapping.get(domain, domain)


def _normalize_domains(student_profile: StudentProfileDict) -> StudentProfileDict:
    """
    recommend_goal/recommend_weekly expect Korean domain labels.
    Accept either Korean or English input and normalize to Korean.
    """
    normalized = dict(student_profile)
    normalized["korean_domain"] = [
        _to_korean_domain(domain, _EN_TO_KR_KOREAN)
        for domain in student_profile.get("korean_domain", [])
        if domain
    ]
    normalized["math_domain"] = [
        _to_korean_domain(domain, _EN_TO_KR_MATH)
        for domain in student_profile.get("math_domain", [])
        if domain
    ]
    return normalized


def _get_openai_key() -> str:
    dotenv.load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing. Set it in your environment or .env file.")
    return api_key


def generate_goal_file_content(student_profile: StudentProfileDict) -> Dict[str, Any]:
    """
    Generate goal JSON using ai_module.recommend_goal without modifying that file.
    Returns a dict shaped like GoalsContent (file_type + annual/semester keys).
    """
    api_key = _get_openai_key()
    normalized_profile = _normalize_domains(student_profile)
    client = recommend_goal.setup_openai_client(api_key)

    relevant_domains = recommend_goal.filter_relevant_goals(normalized_profile)
    goals: Dict[str, Any] = {"file_type": "goal"}

    for domain_name, domain_info in relevant_domains.items():
        ai_result = recommend_goal.generate_goal_for_domain(
            client,
            normalized_profile,
            domain_name,
            domain_info,
        )

        keys = domain_info.get("keys", [])
        if not keys:
            continue

        annual_key = next((k for k in keys if k.startswith("annual_")), keys[0])
        semester_key = next((k for k in keys if k.startswith("semester_")), keys[-1])

        goals[annual_key] = ai_result.annual_goal
        goals[semester_key] = ai_result.semester_goal

    return goals


def generate_weekly_content_file(
    student_profile: StudentProfileDict,
    goals: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Generate weekly content JSON using ai_module.recommend_weekly.
    If goals are not provided, they are generated on the fly via generate_goal_file_content.
    """
    api_key = _get_openai_key()
    normalized_profile = _normalize_domains(student_profile)
    goal_data = goals or generate_goal_file_content(normalized_profile)

    client = recommend_weekly.setup_openai_client(api_key)
    all_domains = recommend_weekly.get_all_domains_info(goal_data)

    weekly_result = recommend_weekly.WeeklyRecommendationResult()

    for domain_info in all_domains.values():
        result_key = f"{domain_info['key_base']}_weeklyContent"

        if domain_info.get("has_both_goals"):
            domain_info_for_llm = {
                "subject": domain_info["subject"],
                "domain_name": domain_info["domain_name"],
                "key_base": domain_info["key_base"],
                "annual_goal": domain_info["annual_goal"],
                "semester_goal": domain_info["semester_goal"],
            }

            weekly_content = recommend_weekly.generate_weekly_content_for_domain(
                client,
                normalized_profile,
                domain_info_for_llm,
            )
            setattr(weekly_result, result_key, weekly_content.weekly_content)
        else:
            setattr(weekly_result, result_key, [])

    return {"file_type": "weekly", **weekly_result.model_dump()}


__all__ = ["generate_goal_file_content", "generate_weekly_content_file"]
