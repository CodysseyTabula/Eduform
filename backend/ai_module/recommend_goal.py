from openai import OpenAI
from pydantic import BaseModel
import dotenv
import os
import json
from typing import List, Dict


# 도메인 이름을 goals 키로 매핑하는 딕셔너리
KOREAN_DOMAIN_MAPPING = {
    "듣기말하기": "listeningSpeaking",
    "읽기": "reading",
    "쓰기": "writing",
    "문법": "grammar",
    "문학": "literature",
    "매체": "mediaLiteracy"
}

MATH_DOMAIN_MAPPING = {
    "수와 연산": "numbersOperations",
    "변화와 관계": "changeAndRelations",
    "도형과 측정": "geometryMeasurement",
    "자료와 가능성": "dataAndProbability"
}


# 1. AI는 annual_goal과 semester_goal만 생성하도록 모델 정의
class GoalContentOnly(BaseModel):
    """AI가 생성할 목표 내용만 포함"""
    annual_goal: str  # 연간 목표 (AI가 생성)
    semester_goal: str  # 학기 목표 (AI가 생성)


# 2. 최종 결과 구조 (domain_name 포함)
class GoalRecommendation(BaseModel):
    """단일 목표 영역의 추천 결과"""
    domain_name: str  # 우리가 정의한 값 (고정)
    annual_goal: str  # AI가 생성한 연간 목표
    semester_goal: str  # AI가 생성한 학기 목표


class GoalRecommendationResult(BaseModel):
    """전체 목표 추천 결과"""
    recommendations: List[GoalRecommendation]


def get_domain_keys(domain_name: str, subject: str) -> List[str]:
    """도메인 이름을 goals 딕셔너리의 키 리스트로 변환"""
    if subject == "korean":
        mapping = KOREAN_DOMAIN_MAPPING
    elif subject == "math":
        mapping = MATH_DOMAIN_MAPPING
    else:
        return []
    
    if domain_name not in mapping:
        return []
    
    key_base = mapping[domain_name]
    return [
        f"annual_{key_base}_goal",
        f"semester_{key_base}_goal"
    ]


def filter_relevant_goals(student_info: Dict) -> Dict[str, List[str]]:
    """student_info의 korean_domain과 math_domain 기반으로 관련 goals 키만 필터링"""
    relevant_goals = {}
    
    # 국어 도메인 처리
    if "korean_domain" in student_info:
        for domain in student_info["korean_domain"]:
            keys = get_domain_keys(domain, "korean")
            if keys:
                relevant_goals[domain] = {
                    "subject": "korean",
                    "keys": keys
                }
    
    # 수학 도메인 처리
    if "math_domain" in student_info:
        for domain in student_info["math_domain"]:
            keys = get_domain_keys(domain, "math")
            if keys:
                relevant_goals[domain] = {
                    "subject": "math",
                    "keys": keys
                }
    
    return relevant_goals


def setup_openai_client(api_key: str) -> OpenAI:
    """OpenAI 클라이언트 설정"""
    return OpenAI(api_key=api_key)


def load_student_info(student_info_path: str) -> Dict:
    """JSON 파일에서 학생 정보 읽기"""
    with open(student_info_path, 'r', encoding='utf-8') as f:
        student_info = json.load(f)
    return student_info


def generate_goal_for_domain(client: OpenAI, student_info: Dict, domain_name: str, domain_info: Dict) -> GoalContentOnly:
    """특정 도메인에 대한 목표 추천 생성 (AI는 annual_goal과 semester_goal만 생성)"""
    
    # 학생 정보 요약 (이름 제외)
    student_summary = f"""
학년: {student_info.get('grade', 'N/A')}학년
학기: {student_info.get('current_semester', 'N/A')}
"""
    
    # 웩슬러 지능검사 결과
    score_info = []
    if 'vci_score' in student_info and student_info.get('vci_score'):
        score_info.append(f"언어 이해 지표(VCI): {student_info['vci_score']}")
    if 'visual_spatial_score' in student_info and student_info.get('visual_spatial_score'):
        score_info.append(f"시공간 지표: {student_info['visual_spatial_score']}")
    if 'fri_score' in student_info and student_info.get('fri_score'):
        score_info.append(f"유동 추론 지표(FRI): {student_info['fri_score']}")
    if 'wmi_score' in student_info and student_info.get('wmi_score'):
        score_info.append(f"작업 기억 지표(WMI): {student_info['wmi_score']}")
    if 'psi_score' in student_info and student_info.get('psi_score'):
        score_info.append(f"처리 속도 지표(PSI): {student_info['psi_score']}")
    if 'fsiq_score' in student_info and student_info.get('fsiq_score'):
        score_info.append(f"전체 지능 지수(FSIQ): {student_info['fsiq_score']}")
    
    if score_info:
        student_summary += "웩슬러 지능검사 결과:\n" + "\n".join(f"  - {s}" for s in score_info) + "\n"
    
    # 현재 수행 수준 정보
    if 'cognitive_level' in student_info and student_info.get('cognitive_level'):
        student_summary += f"\n현재 수행수준 (언어/인지면): {student_info['cognitive_level']}\n"
    if 'social_psych_level' in student_info and student_info.get('social_psych_level'):
        student_summary += f"현재 수행수준 (사회/심리면): {student_info['social_psych_level']}\n"
    if 'motor_daily_level' in student_info and student_info.get('motor_daily_level'):
        student_summary += f"현재 수행수준 (운동/일상생활면): {student_info['motor_daily_level']}\n"
    
    subject_name = "국어" if domain_info["subject"] == "korean" else "수학"
    if domain_info["subject"] == "korean" and 'korean_performance_level' in student_info and student_info.get('korean_performance_level'):
        student_summary += f"\n국어 수행수준: {student_info['korean_performance_level']}\n"
    elif domain_info["subject"] == "math" and 'math_performance_level' in student_info and student_info.get('math_performance_level'):
        student_summary += f"\n수학 수행수준: {student_info['math_performance_level']}\n"
    
    if 'guardian_opinion' in student_info and student_info.get('guardian_opinion'):
        student_summary += f"\n보호자 의견: {student_info['guardian_opinion']}\n"
    
    prompt = f"""
당신은 IEP(개별화교육계획) 설계 지원 서비스의 교육 목표 추천 전문가입니다.

## IEP(개별화교육계획)란?
IEP는 특수교육 대상 학생을 위한 개별화된 교육 계획서입니다. 특수교사는 매 학기마다 각 학생의 수준에 맞는 학습 목표를 설정하고, 이를 바탕으로 주차별 학습 계획을 수립해야 합니다. 이 서비스는 특수교사의 IEP 작성 부담을 줄이고, 학생의 웩슬러 지능검사 결과와 현재 수행수준을 반영하여 최적화된 학습 목표를 제시하는 것을 목적으로 합니다.

## 한국웩슬러 아동용지능검사-5판(K-WISC-V) 해석 가이드

### K-WISC-V 개요
한국웩슬러 아동용지능검사-5판(K-WISC-V)은 만 6세 0개월부터 만 16세 11개월까지 아동의 지능을 평가하기 위해 개별적으로 실시하는 최신판 지능검사 도구입니다. K-WISC-IV의 개정판으로, 4개 영역에서 5개 영역으로 확장되었으며, 16개의 소검사로 구성되어 있습니다. 전반적인 지적능력(FSIQ)은 물론, 특정 인지영역의 지적 기능을 나타내는 5가지 기본지표점수와 5가지 추가지표점수를 제공합니다.

### 5가지 기본지표점수 상세 설명

1. **VCI (Verbal Comprehension Index, 언어이해지표)**
   - **측정 능력**: 언어적 개념형성능력, 언어적 추론능력, 어휘지식, 의사소통능력, 결정지능(후천적으로 학습하고 오랜 시간에 걸쳐 축적한 언어기반지식)
   - **포함 능력**: 지시사항 이해 능력, 언어지식, 사회·과학·문화 전반에 대한 지식, 정보재인능력, 장기기억 인출 능력, 언어적 문제해결 능력
   - **교육적 함의**: 
     - 읽기, 수학, 쓰기의 학업성취와 직접적으로 관련
     - 국어 학습(읽기, 쓰기, 문법)의 핵심 기반 능력
     - 높은 점수: 언어적 설명과 개념 학습에 유리, 추상적 개념 이해 용이
     - 낮은 점수: 시각적 자료, 구체적 예시, 반복 학습, 단계별 언어적 안내 필요

2. **VSI (Visual Spatial Index, 시공간지표)**
   - **측정 능력**: 시각정보와 규칙을 분석하고 조작하는 시공간적 처리능력
   - **포함 능력**: 비언어적 추론능력, 시공간추론능력, 시각-운동처리속도, 시각운동 협응능력, 정신적 회전능력(물체를 머릿속에서 회전시키거나 이동시키는 능력), 시각작업기억, 부분-전체관계 이해
   - **교육적 함의**:
     - 수학 학습(도형, 측정, 공간 개념)과 직접적으로 관련
     - 시공간추론능력과 정신적 회전능력은 수학 학업성취와 관련
     - 높은 점수: 도형 학습, 시각적 자료 활용, 공간 개념 이해에 유리
     - 낮은 점수: 구체적 조작물, 단계별 시각화, 시각-운동 협응 활동 필요

3. **FRI (Fluid Reasoning Index, 유동추론지표)**
   - **측정 능력**: 유동지능(사전지식이나 문화적 기대, 결정지능으로 풀 수 없는 새로운 문제를 해결하는 능력)
   - **특징**: 선천지능에 속하며, 후천적으로 학습된 지식이 아닌 여러 가지 정보와 인지능력을 활용하여 새로운 문제를 해결하는 능력
   - **포함 능력**: 귀납추론능력, 양적추론능력, 추상적 사고능력
   - **교육적 함의**:
     - 수학능력과 직접적으로 관련
     - 수학적 추론능력과 수학적 문제해결능력 발달의 기초
     - 높은 점수: 추상적 개념 이해, 문제 해결 전략 학습, 복잡한 문제 해결에 유리
     - 낮은 점수: 구체적 예시, 단계별 안내, 반복 연습, 패턴 학습 필요

4. **WMI (Working Memory Index, 작업기억지표)**
   - **측정 능력**: 시각, 청각정보를 일시적으로 유지, 조작 및 활용할 수 있는 능력
   - **포함 능력**: 주의집중력, 단기기억, 작업기억, 시연능력, 통제 및 조절능력, 암기력, 순서화 능력, 정신적 통제능력
   - **교육적 함의**:
     - 학습 및 학업성취와 크게 관련되는 기초 능력
     - 모든 학습 영역에 영향을 미치는 핵심 능력
     - 높은 점수: 복잡한 지시 이해, 여러 단계 수행, 정보 조작 및 활용에 유리
     - 낮은 점수: 간단한 지시, 단계별 안내, 즉시 피드백, 정보 분할 제공 필요

5. **PSI (Processing Speed Index, 처리속도지표)**
   - **측정 능력**: 주의를 유지하면서 간단한 과제를 빠르고 정확하게 수행하고, 의사결정을 내릴 수 있는 능력
   - **포함 능력**: 시각운동 협응능력, 시각단기기억, 인지적 유연성, 집중력, 시각적 변별능력, 시각적 탐색능력, 정신운동 속도, 소근육 운동능력, 글씨쓰기 능력, 인지적 처리 속도, 의사결정 속도
   - **교육적 함의**:
     - 읽기와 수학에서의 학업성취와 관련
     - 빠른 처리속도는 일상적인 정보 처리 시간을 단축하고, 복잡한 과제에 인지적 자원을 더 효율적으로 활용 가능
     - 높은 점수: 시간 제한 과제 수행, 빠른 정보 처리에 유리
     - 낮은 점수: 충분한 시간 제공, 과제량 조절, 단계별 수행, 압박감 완화 필요

6. **FSIQ (Full Scale IQ, 전체 지능 지수)**
   - **의미**: 전반적인 지적능력의 종합 지표
   - **교육적 함의**: 전체적인 학습 난이도 조절의 기준

### 점수 해석 기준
- **평균**: 100점 (표준편차 15)
- **85-115점**: 평균 범위
- **70-84점**: 경계선 범위 (학습 지원 필요)
- **55-69점**: 경도 지적장애 범위 (맞춤형 학습 필수)
- **40-54점**: 중도 지적장애 범위 (기초 기능 중심 학습)
- **70점 미만**: 특수교육 대상, 개별화된 접근 필수

### K-WISC-V 결과 활용 방법
- 각 지표의 강점과 약점을 파악하여 학습 방법 조정
- 강점 지표를 활용한 학습 전략 수립 (예: VCI 높음 → 언어적 설명 활용, VSI 높음 → 시각적 자료 활용)
- 약점 지표를 보완하는 학습 지원 제공 (예: WMI 낮음 → 단계별 안내, PSI 낮음 → 시간 충분히 제공)
- 점수에 따라 학습 난이도, 속도, 방법을 개별화
- 지표 간 차이를 분석하여 학습 전략 조정

## 목표 설정 규칙
1. **연간 목표**: 해당 영역에 대한 1년간(1학기+2학기)의 종합적인 학습 목표입니다. 연간 목표는 1학기와 2학기가 동일하게 유지됩니다.
2. **학기 목표**: 현재 학기에 달성할 구체적이고 측정 가능한 학습 목표입니다. 과목별로 여러 영역(예: 수와연산, 도형과측정 등)으로 세분화되어 설정됩니다.
3. 목표는 국가 교육과정 성취기준을 기반으로 하되, 학생의 현재 수행수준과 웩슬러 지능검사 결과를 반영하여 적절한 난이도로 조정해야 합니다.
4. 목표는 구체적이고 측정 가능하며, 실제 수업에서 달성 가능한 수준으로 작성해야 합니다.

## 학생 정보
{student_summary}

## 목표 설정 요청
목표 영역: {subject_name} - {domain_name}

위 학생 정보를 바탕으로 다음을 작성해주세요:
1. **연간 목표**: {domain_name} 영역에 대한 1년간의 종합적인 학습 목표 (2-3문장, 구체적이고 측정 가능하게)
2. **학기 목표**: 현재 학기에 {domain_name} 영역에서 달성할 구체적인 학습 목표 (2-3문장, 구체적이고 측정 가능하게)

**중요 지침:**
- **웩슬러 지능검사 결과를 반드시 고려하세요:**
  - 각 지표의 점수를 분석하여 학생의 강점과 약점을 파악하세요
  - 국어 영역: VCI 점수를 특히 중요하게 고려하세요
  - 수학 영역: VSI, FRI 점수를 특히 중요하게 고려하세요
  - WMI와 PSI 점수는 모든 영역의 학습 방법과 속도 조절에 반영하세요
  - 점수가 낮은 지표가 있는 경우, 해당 능력을 보완하는 목표를 포함하거나 학습 방법을 조정하세요
- 학생의 현재 수행수준을 반영하여 적절한 난이도로 설정하세요
- 목표는 국가 교육과정 성취기준을 기반으로 하되, 학생의 개별 특성을 고려하여 조정하세요
- 목표 작성 시 학생의 이름이나 개인 식별 정보는 절대 포함하지 마세요. 일반적인 표현으로 작성하세요
- 목표는 구체적이고 측정 가능하며, 실제 수업에서 달성 가능한 수준으로 작성하세요

응답 형식:
annual_goal과 semester_goal 필드에 목표 내용만 포함해주세요.
"연간 목표:", "학기 목표:" 같은 라벨이나 접두사는 절대 포함하지 마세요.
순수하게 목표 내용만 작성해주세요.

잘못된 예시 (하지 마세요):
annual_goal: "연간 목표: 학생이 읽기 능력을 향상시킨다."
semester_goal: "학기 목표: 학생이 단어를 정확히 읽을 수 있다."

올바른 예시 (이렇게 작성하세요):
annual_goal: "읽기 능력을 향상시킨다."
semester_goal: "단어를 정확히 읽을 수 있다."
"""
    
    response = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[{"role": "user", "content": prompt}],
        response_format=GoalContentOnly  # AI는 annual_goal과 semester_goal만 생성
    )
    
    return response.choices[0].message.parsed


def print_goal_recommendations(result: GoalRecommendationResult, student_info: Dict):
    """목표 추천 결과 출력"""
    print("=" * 60)
    print("AI 목표 추천 결과")
    print("=" * 60)
    print(f"\n학생: {student_info.get('name', 'N/A')} ({student_info.get('grade', 'N/A')}학년 {student_info.get('current_semester', 'N/A')})")
    print(f"\n추천된 목표:")
    
    for i, rec in enumerate(result.recommendations, 1):
        print(f"\n[{i}] {rec.domain_name}")
        print(f"    연간 목표: {rec.annual_goal}")
        print(f"    학기 목표: {rec.semester_goal}")
    
    print("\n" + "=" * 60)


def main():
    # 환경 변수 로드
    dotenv.load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not openai_api_key:
        print("오류: OPENAI_API_KEY가 설정되지 않았습니다.")
        return
    
    # OpenAI 클라이언트 설정
    openai_client = setup_openai_client(openai_api_key)
    
    # JSON 파일에서 학생 정보 읽기
    student_info_path = "student_info.json"
    
    try:
        student_info = load_student_info(student_info_path)
    except FileNotFoundError:
        print(f"오류: 파일을 찾을 수 없습니다. {student_info_path}")
        return
    except json.JSONDecodeError as e:
        print(f"오류: JSON 파일 파싱 실패. {e}")
        return
    
    goals = {
        "annual_listeningSpeaking_goal": "",
        "semester_listeningSpeaking_goal": "",
        "annual_reading_goal": "",
        "semester_reading_goal": "",
        "annual_writing_goal": "",
        "semester_writing_goal": "",
        "annual_grammar_goal": "",
        "semester_grammar_goal": "",
        "annual_literature_goal": "",
        "semester_literature_goal": "",
        "annual_mediaLiteracy_goal": "",
        "semester_mediaLiteracy_goal": "",
        "annual_numbersOperations_goal": "",
        "semester_numbersOperations_goal": "",
        "annual_changeAndRelations_goal": "",
        "semester_changeAndRelations_goal": "",
        "annual_geometryMeasurement_goal": "",
        "semester_geometryMeasurement_goal": "",
        "annual_dataAndProbability_goal": "",
        "semester_dataAndProbability_goal": ""
    }
    
    print("=" * 60)
    print("AI 기반 교육 목표 추천")
    print("=" * 60)
    print(f"\n학생 정보:")
    print(f"  이름: {student_info.get('name', 'N/A')}")
    print(f"  학년: {student_info.get('grade', 'N/A')}학년")
    print(f"  학기: {student_info.get('current_semester', 'N/A')}")
    print(f"  국어 영역: {', '.join(student_info.get('korean_domain', []))}")
    print(f"  수학 영역: {', '.join(student_info.get('math_domain', []))}")
    
    try:
        # 1. 관련 목표 필터링
        print(f"\n관련 목표 영역 필터링 중...")
        relevant_domains = filter_relevant_goals(student_info)
        if not relevant_domains:
            print("추천할 목표 영역이 없습니다.")
            return
        
        print(f"{len(relevant_domains)}개의 목표 영역을 찾았습니다:")
        for domain_name in relevant_domains.keys():
            print(f"  - {domain_name}")
        
        # 2. 목표 추천 생성 (각 도메인별로 개별 호출)
        print(f"\nAI 목표 추천 생성 중...")
        recommendations_list = []
        
        for domain_name, domain_info in relevant_domains.items():
            print(f"  - {domain_name} 처리 중...")
            # AI는 annual_goal과 semester_goal만 생성
            ai_result = generate_goal_for_domain(openai_client, student_info, domain_name, domain_info)
            
            # 3. 코드에서 domain_name을 직접 추가 (우리가 정의한 값으로 고정)
            final_result = GoalRecommendation(
                domain_name=domain_name,  # 우리가 정의한 값 → 절대 변하지 않음
                annual_goal=ai_result.annual_goal,  # AI가 생성한 내용
                semester_goal=ai_result.semester_goal  # AI가 생성한 내용
            )
            recommendations_list.append(final_result)
        
        # 결과를 GoalRecommendationResult 구조로 변환
        result = GoalRecommendationResult(recommendations=recommendations_list)

        # 4. 결과 출력
        print_goal_recommendations(result, student_info)
        
        # 5. goals 딕셔너리에 결과 반영
        print(f"\n목표 딕셔너리에 결과 반영 중...")
        for rec in result.recommendations:
            # domain_name은 우리가 정의한 정확한 값이므로 매칭이 보장됨
            domain_info = relevant_domains.get(rec.domain_name)
            if domain_info:
                keys = domain_info["keys"]
                if len(keys) >= 2:
                    # annual_goal과 semester_goal 키 찾기
                    annual_key = keys[0] if "annual" in keys[0] else keys[1]
                    semester_key = keys[1] if "semester" in keys[1] else keys[0]
                    
                    if annual_key in goals:
                        goals[annual_key] = rec.annual_goal
                    if semester_key in goals:
                        goals[semester_key] = rec.semester_goal
        
        # 6. JSON 출력
        print("\nJSON 형식:")
        print(json.dumps(result.model_dump(), ensure_ascii=False, indent=2))
        
        print("\n업데이트된 goals 딕셔너리:")
        print(json.dumps(goals, ensure_ascii=False, indent=2))
    # goals 변수를 JSON 파일로 저장 (file_type을 첫 번째 키로 추가)
        output_data = {"file_type": "goal"}
        output_data.update(goals)
        with open("goals.json", "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
            print("\ngoals.json 파일로 저장 완료!")
    except Exception as e:
            print(f"\n오류 발생: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()