#!/usr/bin/env python3
"""
새로운 AI 모듈 파일들 테스트

recommend_goal.py, recommend_weekly.py, recommend_weekly_material.py의
기본 구조와 import를 확인합니다.
"""

import sys
import os
from pathlib import Path

# 부모 디렉토리(backend)를 경로에 추가
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

print("=" * 60)
print("새로운 AI 모듈 파일들 테스트")
print("=" * 60)

# 1. recommend_goal.py 테스트
print("\n[1] recommend_goal.py 테스트...")
try:
    import ai_module.recommend_goal as rg
    
    # 주요 함수들이 있는지 확인
    assert hasattr(rg, 'setup_openai_client'), "setup_openai_client 함수가 없음"
    assert hasattr(rg, 'load_student_info'), "load_student_info 함수가 없음"
    assert hasattr(rg, 'filter_relevant_goals'), "filter_relevant_goals 함수가 없음"
    assert hasattr(rg, 'generate_goal_for_domain'), "generate_goal_for_domain 함수가 없음"
    assert hasattr(rg, 'main'), "main 함수가 없음"
    
    # 도메인 매핑 확인
    assert hasattr(rg, 'KOREAN_DOMAIN_MAPPING'), "KOREAN_DOMAIN_MAPPING이 없음"
    assert hasattr(rg, 'MATH_DOMAIN_MAPPING'), "MATH_DOMAIN_MAPPING이 없음"
    
    print("  ✓ 모든 함수와 상수 존재 확인")
    print(f"  ✓ 국어 도메인: {len(rg.KOREAN_DOMAIN_MAPPING)}개")
    print(f"  ✓ 수학 도메인: {len(rg.MATH_DOMAIN_MAPPING)}개")
    
    # filter_relevant_goals 함수 테스트 (API 호출 없이)
    test_student_info = {
        "name": "테스트",
        "grade": 1,
        "korean_domain": ["읽기", "쓰기"],
        "math_domain": ["수와 연산"]
    }
    
    relevant_goals = rg.filter_relevant_goals(test_student_info)
    assert isinstance(relevant_goals, dict), "filter_relevant_goals 결과가 딕셔너리가 아님"
    assert len(relevant_goals) == 3, f"예상된 도메인 수와 다름 (예상: 3, 실제: {len(relevant_goals)})"
    print(f"  ✓ filter_relevant_goals 테스트 통과: {len(relevant_goals)}개 도메인 필터링")
    
except ImportError as e:
    print(f"  ✗ Import 실패: {e}")
    print("    필요한 패키지: openai, pydantic, python-dotenv")
except Exception as e:
    print(f"  ✗ 오류: {e}")
    import traceback
    traceback.print_exc()

# 2. recommend_weekly.py 테스트
print("\n[2] recommend_weekly.py 테스트...")
try:
    import ai_module.recommend_weekly as rw
    
    # 주요 함수들이 있는지 확인
    assert hasattr(rw, 'setup_openai_client'), "setup_openai_client 함수가 없음"
    assert hasattr(rw, 'load_student_info_and_goals'), "load_student_info_and_goals 함수가 없음"
    assert hasattr(rw, 'get_domains_with_goals'), "get_domains_with_goals 함수가 없음"
    assert hasattr(rw, 'generate_weekly_content_for_domain'), "generate_weekly_content_for_domain 함수가 없음"
    assert hasattr(rw, 'main'), "main 함수가 없음"
    
    # 도메인 매핑 확인
    assert hasattr(rw, 'KOREAN_DOMAIN_MAPPING'), "KOREAN_DOMAIN_MAPPING이 없음"
    assert hasattr(rw, 'MATH_DOMAIN_MAPPING'), "MATH_DOMAIN_MAPPING이 없음"
    
    print("  ✓ 모든 함수와 상수 존재 확인")
    
    # get_domains_with_goals 함수 테스트 (API 호출 없이)
    test_goals = {
        "file_type": "goal",
        "annual_reading_goal": "연간 읽기 목표",
        "semester_reading_goal": "학기 읽기 목표",
        "annual_numbersOperations_goal": "연간 수와 연산 목표",
        "semester_numbersOperations_goal": "학기 수와 연산 목표"
    }
    
    domains_with_goals = rw.get_domains_with_goals(test_goals)
    assert isinstance(domains_with_goals, dict), "get_domains_with_goals 결과가 딕셔너리가 아님"
    print(f"  ✓ get_domains_with_goals 테스트 통과: {len(domains_with_goals)}개 도메인 발견")
    
except ImportError as e:
    print(f"  ✗ Import 실패: {e}")
    print("    필요한 패키지: openai, pydantic, python-dotenv")
except Exception as e:
    print(f"  ✗ 오류: {e}")
    import traceback
    traceback.print_exc()

# 3. recommend_weekly_material.py 테스트
print("\n[3] recommend_weekly_material.py 테스트...")
try:
    import ai_module.recommend_weekly_material as rwm
    
    # 주요 함수들이 있는지 확인
    assert hasattr(rwm, 'setup_pinecone'), "setup_pinecone 함수가 없음"
    assert hasattr(rwm, 'load_embedding_model'), "load_embedding_model 함수가 없음"
    assert hasattr(rwm, 'setup_openai_client'), "setup_openai_client 함수가 없음"
    assert hasattr(rwm, 'load_weekly_content'), "load_weekly_content 함수가 없음"
    assert hasattr(rwm, 'generate_weekly_materials'), "generate_weekly_materials 함수가 없음"
    assert hasattr(rwm, 'main'), "main 함수가 없음"
    
    # 도메인 매핑 확인
    assert hasattr(rwm, 'KOREAN_DOMAIN_MAPPING'), "KOREAN_DOMAIN_MAPPING이 없음"
    assert hasattr(rwm, 'MATH_DOMAIN_MAPPING'), "MATH_DOMAIN_MAPPING이 없음"
    
    print("  ✓ 모든 함수와 상수 존재 확인")
    
except ImportError as e:
    print(f"  ✗ Import 실패: {e}")
    print("    필요한 패키지: pinecone, sentence-transformers, openai, pydantic, python-dotenv")
except Exception as e:
    print(f"  ✗ 오류: {e}")
    import traceback
    traceback.print_exc()

# 4. 필요한 패키지 확인
print("\n[4] 필요한 패키지 확인...")
required_packages = {
    'openai': 'OpenAI API 클라이언트',
    'pydantic': '데이터 검증',
    'dotenv': '환경 변수 로드',
    'pinecone': '벡터 데이터베이스 (recommend_weekly_material.py용)',
    'sentence_transformers': '임베딩 모델 (recommend_weekly_material.py용)'
}

missing_packages = []
for package, description in required_packages.items():
    try:
        __import__(package)
        print(f"  ✓ {package}: 설치됨")
    except ImportError:
        print(f"  ✗ {package}: 설치 필요 ({description})")
        missing_packages.append(package)

if missing_packages:
    print(f"\n경고: 다음 패키지들이 설치되지 않았습니다:")
    for pkg in missing_packages:
        print(f"  - {pkg}")
    print("\n설치 명령어:")
    print(f"  pip install {' '.join(missing_packages)}")
else:
    print("\n  ✓ 모든 필수 패키지가 설치되어 있습니다!")

print("\n" + "=" * 60)
print("테스트 완료")
print("=" * 60)

