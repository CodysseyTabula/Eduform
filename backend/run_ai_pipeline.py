#!/usr/bin/env python3
"""
AI 모듈 전체 파이프라인 실행 스크립트

3단계를 순차적으로 실행합니다:
1. 목표 생성 (recommend_goal.py)
2. 주차별 학습 내용 생성 (recommend_weekly.py)
3. 주차별 학습 자료 추천 (recommend_weekly_material.py)
"""

import sys
import os
import subprocess
from pathlib import Path

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))


def check_file_exists(filepath: str) -> bool:
    """파일 존재 여부 확인"""
    return Path(filepath).exists()


def run_step(step_name: str, module_name: str, required_files: list[str]) -> bool:
    """각 단계 실행"""
    print("=" * 60)
    print(f"[{step_name}] 실행 중...")
    print("=" * 60)
    
    # 필수 파일 확인
    missing_files = [f for f in required_files if not check_file_exists(f)]
    if missing_files:
        print(f"❌ 오류: 다음 파일들이 없습니다:")
        for f in missing_files:
            print(f"   - {f}")
        return False
    
    print(f"✓ 필수 파일 확인 완료: {', '.join(required_files)}")
    print()
    
    # 모듈 실행
    try:
        result = subprocess.run(
            [sys.executable, "-m", module_name],
            cwd=Path(__file__).parent,
            check=True,
            capture_output=False
        )
        print()
        print(f"✓ [{step_name}] 완료!")
        return True
    except subprocess.CalledProcessError as e:
        print()
        print(f"❌ [{step_name}] 실패: {e}")
        return False
    except KeyboardInterrupt:
        print()
        print(f"⚠️  [{step_name}] 사용자에 의해 중단됨")
        return False


def main():
    """전체 파이프라인 실행"""
    print("=" * 60)
    print("AI 모듈 전체 파이프라인 실행")
    print("=" * 60)
    print()
    
    # 환경 변수 확인
    from dotenv import load_dotenv
    load_dotenv()
    
    openai_key = os.getenv("OPENAI_API_KEY")
    pinecone_key = os.getenv("PINECONE_API_KEY")
    
    if not openai_key:
        print("❌ 오류: OPENAI_API_KEY가 설정되지 않았습니다.")
        print("   .env 파일에 OPENAI_API_KEY를 추가하세요.")
        return False
    
    if not pinecone_key:
        print("⚠️  경고: PINECONE_API_KEY가 설정되지 않았습니다.")
        print("   3단계(학습 자료 추천)는 실행되지 않습니다.")
        print()
    
    # 1단계: 목표 생성
    if not run_step(
        "1단계: 목표 생성",
        "ai_module.recommend_goal",
        ["student_info.json"]
    ):
        return False
    
    # 2단계: 주차별 학습 내용 생성
    if not run_step(
        "2단계: 주차별 학습 내용 생성",
        "ai_module.recommend_weekly",
        ["student_info.json", "goals.json"]
    ):
        return False
    
    # 3단계: 주차별 학습 자료 추천 (Pinecone 필요)
    if pinecone_key:
        if not run_step(
            "3단계: 주차별 학습 자료 추천",
            "ai_module.recommend_weekly_material",
            ["weekly_content.json"]
        ):
            return False
    else:
        print()
        print("=" * 60)
        print("[3단계: 주차별 학습 자료 추천] 건너뜀")
        print("=" * 60)
        print("PINECONE_API_KEY가 설정되지 않아 건너뜁니다.")
        print()
    
    # 완료 메시지
    print("=" * 60)
    print("✅ 전체 파이프라인 완료!")
    print("=" * 60)
    print()
    print("생성된 파일:")
    if check_file_exists("goals.json"):
        print("  ✓ goals.json")
    if check_file_exists("weekly_content.json"):
        print("  ✓ weekly_content.json")
    if check_file_exists("weekly_material_recommendations.json"):
        print("  ✓ weekly_material_recommendations.json")
    print()
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  사용자에 의해 중단되었습니다.")
        sys.exit(1)

