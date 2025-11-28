from openai import OpenAI
from pydantic import BaseModel
import dotenv
import os
import json
from typing import List, Dict, Tuple


# 도메인 이름을 goals 키로 매핑하는 딕셔너리 (recommend_goal.py에서 재사용)
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

# 역매핑: goals 키에서 도메인 이름으로
GOAL_KEY_TO_DOMAIN = {}
for domain_name, key_base in KOREAN_DOMAIN_MAPPING.items():
    GOAL_KEY_TO_DOMAIN[f"annual_{key_base}_goal"] = ("korean", domain_name)
    GOAL_KEY_TO_DOMAIN[f"semester_{key_base}_goal"] = ("korean", domain_name)
for domain_name, key_base in MATH_DOMAIN_MAPPING.items():
    GOAL_KEY_TO_DOMAIN[f"annual_{key_base}_goal"] = ("math", domain_name)
    GOAL_KEY_TO_DOMAIN[f"semester_{key_base}_goal"] = ("math", domain_name)

# 주차 번호 리스트 (1~20주차 고정)
WEEK_LABELS = [f"{i}주차" for i in range(1, 21)]  # ["1주차", "2주차", ..., "20주차"]


# Pydantic 모델 정의
class WeeklyContentResult(BaseModel):
    """단일 도메인의 20주차 학습 내용"""
    weekly_content: List[str]  # 20개 문자열 배열


class WeeklyDomainContent(BaseModel):
    """단일 도메인의 주차별 학습 내용 결과"""
    domain_key: str  # 예: "listeningSpeaking_weeklyContent"
    weekly_content: List[str]  # 20개 문자열 배열


class WeeklyRecommendationResult(BaseModel):
    """전체 주차별 학습 내용 추천 결과"""
    listeningSpeaking_weeklyContent: List[str] = []
    reading_weeklyContent: List[str] = []
    writing_weeklyContent: List[str] = []
    grammar_weeklyContent: List[str] = []
    literature_weeklyContent: List[str] = []
    mediaLiteracy_weeklyContent: List[str] = []
    numbersOperations_weeklyContent: List[str] = []
    changeAndRelations_weeklyContent: List[str] = []
    geometryMeasurement_weeklyContent: List[str] = []
    dataAndProbability_weeklyContent: List[str] = []


def setup_openai_client(api_key: str) -> OpenAI:
    """OpenAI 클라이언트 설정"""
    return OpenAI(api_key=api_key)


def load_student_info_and_goals(student_info_path: str, goals_path: str) -> Tuple[Dict, Dict]:
    """JSON 파일에서 학생 정보와 목표 읽기"""
    with open(student_info_path, 'r', encoding='utf-8') as f:
        student_info = json.load(f)

    with open(goals_path, 'r', encoding='utf-8') as f:
        goals = json.load(f)

    return student_info, goals


def get_all_domains_info(goals: Dict) -> Dict[str, Dict]:
    """모든 도메인 정보를 반환 (목표가 있는 도메인과 없는 도메인 모두 포함)"""
    all_domains = {}

    # 국어 도메인 처리
    for domain_name, key_base in KOREAN_DOMAIN_MAPPING.items():
        domain_id = f"korean_{domain_name}"
        annual_key = f"annual_{key_base}_goal"
        semester_key = f"semester_{key_base}_goal"

        annual_goal = goals.get(annual_key, "").strip()
        semester_goal = goals.get(semester_key, "").strip()

        all_domains[domain_id] = {
            "subject": "korean",
            "domain_name": domain_name,
            "key_base": key_base,
            "annual_goal": annual_goal,
            "semester_goal": semester_goal,
            "has_both_goals": bool(annual_goal and semester_goal)
        }

    # 수학 도메인 처리
    for domain_name, key_base in MATH_DOMAIN_MAPPING.items():
        domain_id = f"math_{domain_name}"
        annual_key = f"annual_{key_base}_goal"
        semester_key = f"semester_{key_base}_goal"

        annual_goal = goals.get(annual_key, "").strip()
        semester_goal = goals.get(semester_key, "").strip()

        all_domains[domain_id] = {
            "subject": "math",
            "domain_name": domain_name,
            "key_base": key_base,
            "annual_goal": annual_goal,
            "semester_goal": semester_goal,
            "has_both_goals": bool(annual_goal and semester_goal)
        }

    return all_domains


def get_domains_with_goals(goals: Dict) -> Dict[str, Dict]:
    """목표가 설정된 도메인만 필터링하여 반환 (연간/학기 목표 모두 있는 경우만)"""
    all_domains = get_all_domains_info(goals)
    domains_with_goals = {}

    for domain_id, domain_info in all_domains.items():
        if domain_info["has_both_goals"]:
            # has_both_goals 필드 제거 (LLM 호출 시 필요 없음)
            domain_info_copy = {k: v for k, v in domain_info.items() if k != "has_both_goals"}
            domains_with_goals[domain_id] = domain_info_copy

    return domains_with_goals


def create_student_summary(student_info: Dict) -> str:
    """학생 정보 요약 생성"""
    summary = f"""
학년: {student_info.get('grade', 'N/A')}학년
"""

    if 'birth' in student_info:
        summary += f"생년월일: {student_info['birth']}\n"

    if 'guardian_opinion' in student_info and student_info['guardian_opinion']:
        summary += f"보호자 의견: {student_info['guardian_opinion']}\n"

    if 'cognitive_level' in student_info and student_info['cognitive_level']:
        summary += f"현재 수행수준 (언어/인지면): {student_info['cognitive_level']}\n"

    if 'social_psych_level' in student_info and student_info['social_psych_level']:
        summary += f"현재 수행수준 (사회/심리면): {student_info['social_psych_level']}\n"

    if 'motor_daily_level' in student_info and student_info['motor_daily_level']:
        summary += f"현재 수행수준 (운동/일상생활면): {student_info['motor_daily_level']}\n"

    # 지능 지표 점수
    score_info = []
    if 'vci_score' in student_info and student_info['vci_score']:
        score_info.append(f"언어 이해 지표(VCI): {student_info['vci_score']}")
    if 'visual_spatial_score' in student_info and student_info['visual_spatial_score']:
        score_info.append(f"시공간 지표: {student_info['visual_spatial_score']}")
    if 'fri_score' in student_info and student_info['fri_score']:
        score_info.append(f"유동 추론 지표(FRI): {student_info['fri_score']}")
    if 'wmi_score' in student_info and student_info['wmi_score']:
        score_info.append(f"작업 기억 지표(WMI): {student_info['wmi_score']}")
    if 'psi_score' in student_info and student_info['psi_score']:
        score_info.append(f"처리 속도 지표(PSI): {student_info['psi_score']}")
    if 'fsiq_score' in student_info and student_info['fsiq_score']:
        score_info.append(f"전체 지능 지수(FSIQ): {student_info['fsiq_score']}")

    if score_info:
        summary += "지능 지표:\n" + "\n".join(f"  - {s}" for s in score_info) + "\n"

    if 'korean_performance_level' in student_info and student_info['korean_performance_level']:
        summary += f"국어 수행수준: {student_info['korean_performance_level']}\n"

    if 'math_performance_level' in student_info and student_info['math_performance_level']:
        summary += f"수학 수행수준: {student_info['math_performance_level']}\n"

    return summary.strip()


def format_weekly_content(content_list: List[str]) -> List[str]:
    """주차별 학습 내용에 주차 번호를 추가"""
    formatted_list = []

    for week_label, content in zip(WEEK_LABELS, content_list):
        # WEEK_LABELS에서 가져온 주차 번호로 형식화: "1주차: " + 내용
        formatted_content = f"{week_label}: {content.strip()}"
        formatted_list.append(formatted_content)

    return formatted_list


def generate_weekly_content_for_domain(
    client: OpenAI,
    student_info: Dict,
    domain_info: Dict
) -> WeeklyContentResult:
    """특정 도메인에 대한 20주차 학습 내용 생성"""

    student_summary = create_student_summary(student_info)
    subject_name = "국어" if domain_info["subject"] == "korean" else "수학"
    domain_name = domain_info["domain_name"]
    annual_goal = domain_info["annual_goal"]
    semester_goal = domain_info["semester_goal"]

    prompt = f"""
당신은 IEP(개별화교육계획) 설계 지원 서비스의 주차별 학습 내용 생성 전문가입니다.
STRONG RULE : **주의사항 모든 언어는 한국어로 작성하세요.**
## IEP(개별화교육계획)란?
IEP는 특수교육 대상 학생을 위한 개별화된 교육 계획서입니다. 특수교사는 매 학기마다 각 학생의 수준에 맞는 학습 목표를 설정하고, 이를 바탕으로 주차별 학습 계획을 수립해야 합니다. 이 서비스는 특수교사의 IEP 작성 부담을 줄이고, 학생의 웩슬러 지능검사 결과와 현재 수행수준을 반영하여 최적화된 학습 계획을 제시하는 것을 목적으로 합니다.
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
## 주차별 학습 내용의 역할
주차별 학습 내용은 확정된 학습 목표를 바탕으로 학기 주차(20주)별로 "무엇을 배울지"를 텍스트로 표현한 추상적인 학습 주제/내용입니다. 이는 아직 구체적인 학습 자료(교과서, 활동자료, 보조 자료 등)가 매핑되기 전 단계로, 각 주차의 학습 방향과 주제를 명확히 제시하는 역할을 합니다. 이후 이 학습 내용 텍스트와 유사도가 높은 학습 자료가 자동으로 추천되어 매핑됩니다.
## 프로세스
1. 연간 목표 및 학기 목표 확정
2. 주차별 학습 내용(텍스트) 생성 ← **현재 단계**
3. 학습 내용과 유사한 학습 자료 자동 매핑 (후속 단계)
## 학생 정보
{student_summary}
## 목표 정보
목표 영역: {subject_name} - {domain_name}
연간 목표: {annual_goal}
학기 목표: {semester_goal}
## 주차별 학습 내용 생성 요청
위 학생 정보와 목표를 바탕으로 총 20주차에 걸친 주차별 학습 내용을 생성해주세요.
**요구사항:**
1. 총 20주차에 대한 주차별 학습 내용을 생성해주세요.
2. 각 주차별 학습 내용은 1-2문장으로 구체적이고 실현 가능하게 작성해주세요.
3. 학습 내용은 학기 목표를 달성하기 위해 점진적으로 발전하도록 구성해주세요.
4. 초반 주차(1-7주차)는 기초를 다지고, 중반 주차(8-14주차)는 심화 학습, 후반 주차(15-20주차)는 종합 및 평가로 구성해주세요.
5. **웩슬러 지능검사 결과를 반드시 고려하세요:**
   - 국어 영역: VCI 점수를 특히 중요하게 고려하여, 낮은 경우 시각적 자료 활용, 구체적 예시, 반복 학습을 포함하세요
   - 수학 영역: VSI, FRI 점수를 특히 중요하게 고려하여, 낮은 경우 구체적 조작물, 단계별 시각화, 반복 연습을 포함하세요
   - WMI가 낮은 경우: 간단한 단계, 즉시 피드백, 단계별 안내를 포함하세요
   - PSI가 낮은 경우: 충분한 시간 제공, 과제량 조절을 고려한 학습 내용을 포함하세요
   - 각 지표의 강점을 활용한 학습 방법을 반영하세요
6. 학생의 현재 수행수준을 반영하여 적절한 난이도로 설정해주세요.
7. 국가 교육과정 성취기준을 기반으로 하되, 학생의 개별 특성을 고려하여 조정하세요.
8. **중요: 학습 내용 작성 시 학생의 이름이나 개인 식별 정보는 절대 포함하지 마세요. 일반적인 표현으로 작성하세요.**
9. **매우 중요: 주차 번호를 절대 포함하지 마세요. "1주차", "2주차", "**1주차:**", "1주차:" 같은 어떤 형식의 주차 번호도 포함하지 마세요. 순수한 학습 목표/내용만 작성하세요.**
**응답 형식:**
weekly_content 필드에 20개의 문자열 배열을 포함해주세요. 각 문자열은 순수한 학습 목표나 학습 내용만 포함해야 하며, 주차 번호나 주차 관련 표현은 전혀 포함하지 마세요.
**예시 (올바른 형식):**
- "다양한 주제의 짧은 글을 읽고 내용 요약하기 연습"
- "주어진 글을 읽고 이해한 내용을 친구와 서로 설명해보기"
- "간단한 주제에 대해 한 문장으로 자신의 생각을 표현하기"
**예시 (잘못된 형식 - 절대 사용하지 마세요):**
- "1주차: 다양한 주제의 짧은 글을 읽고 내용 요약하기 연습"
- "**1주차:** 다양한 주제의 짧은 글을 읽고 내용 요약하기 연습"
"""

    response = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[{"role": "user", "content": prompt}],
        response_format=WeeklyContentResult
    )

    return response.choices[0].message.parsed


def print_weekly_recommendations(result: WeeklyRecommendationResult, student_info: Dict):
    """주차별 학습 내용 추천 결과 출력"""
    print("=" * 60)
    print("AI 주차별 학습 내용 추천 결과")
    print("=" * 60)
    print(f"\n학생: {student_info.get('name', 'N/A')} ({student_info.get('grade', 'N/A')}학년)")

    # 국어 도메인 출력
    korean_domains = [
        ("listeningSpeaking_weeklyContent", "듣기말하기"),
        ("reading_weeklyContent", "읽기"),
        ("writing_weeklyContent", "쓰기"),
        ("grammar_weeklyContent", "문법"),
        ("literature_weeklyContent", "문학"),
        ("mediaLiteracy_weeklyContent", "매체")
    ]

    print("\n[국어 영역]")
    for key, domain_name in korean_domains:
        content = getattr(result, key, [])
        if content:
            print(f"\n{domain_name}:")
            for week, week_content in enumerate(content, 1):
                print(f"  {week}주차: {week_content}")

    # 수학 도메인 출력
    math_domains = [
        ("numbersOperations_weeklyContent", "수와 연산"),
        ("changeAndRelations_weeklyContent", "변화와 관계"),
        ("geometryMeasurement_weeklyContent", "도형과 측정"),
        ("dataAndProbability_weeklyContent", "자료와 가능성")
    ]

    print("\n[수학 영역]")
    for key, domain_name in math_domains:
        content = getattr(result, key, [])
        if content:
            print(f"\n{domain_name}:")
            for week, week_content in enumerate(content, 1):
                print(f"  {week}주차: {week_content}")

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

    # JSON 파일에서 데이터 읽기
    # 기본 파일명 (필요시 수정 가능)
    student_info_path = "student_info.json"
    goals_path = "goals.json"

    try:
        student_info, goals = load_student_info_and_goals(student_info_path, goals_path)
    except FileNotFoundError as e:
        print(f"오류: 파일을 찾을 수 없습니다. {e}")
        print(f"다음 파일들이 필요합니다:")
        print(f"  - {student_info_path}")
        print(f"  - {goals_path}")
        return
    except json.JSONDecodeError as e:
        print(f"오류: JSON 파일 파싱 실패. {e}")
        return

    print("=" * 60)
    print("AI 기반 주차별 학습 내용 추천")
    print("=" * 60)
    print(f"\n학생 정보:")
    print(f"  이름: {student_info.get('name', 'N/A')}")
    print(f"  학년: {student_info.get('grade', 'N/A')}학년")

    try:
        # 1. 목표가 있는 도메인 필터링
        print(f"\n목표가 설정된 도메인 필터링 중...")
        domains_with_goals = get_domains_with_goals(goals)

        if not domains_with_goals:
            print("목표가 설정된 도메인이 없습니다.")
            return

        print(f"{len(domains_with_goals)}개의 도메인을 찾았습니다:")
        for domain_id, domain_info in domains_with_goals.items():
            print(f"  - {domain_info['subject']} - {domain_info['domain_name']}")

        # 2. 모든 도메인 정보 가져오기 (목표 유무 확인용)
        all_domains = get_all_domains_info(goals)

        # 3. 각 도메인별로 주차별 학습 내용 생성 (목표가 있는 도메인만 LLM 호출)
        print(f"\nAI 주차별 학습 내용 생성 중...")
        result = WeeklyRecommendationResult()

        for domain_id, domain_info in all_domains.items():
            subject = domain_info["subject"]
            domain_name = domain_info["domain_name"]
            key_base = domain_info["key_base"]
            has_both_goals = domain_info["has_both_goals"]

            result_key = f"{key_base}_weeklyContent"

            if has_both_goals:
                # 연간/학기 목표가 모두 있는 경우만 LLM 호출
                print(f"  - {subject} - {domain_name} 처리 중...")

                # LLM 호출을 위한 도메인 정보 준비 (has_both_goals 제외)
                domain_info_for_llm = {
                    "subject": subject,
                    "domain_name": domain_name,
                    "key_base": key_base,
                    "annual_goal": domain_info["annual_goal"],
                    "semester_goal": domain_info["semester_goal"]
                }

                weekly_result = generate_weekly_content_for_domain(
                    openai_client,
                    student_info,
                    domain_info_for_llm
                )

                # LLM이 생성한 순수한 학습 내용을 직접 사용 (주차 번호 없음)
                # 결과를 WeeklyRecommendationResult에 반영
                if hasattr(result, result_key):
                    setattr(result, result_key, weekly_result.weekly_content)
                else:
                    print(f"    경고: {result_key} 필드를 찾을 수 없습니다.")
            else:
                # 목표가 없는 도메인은 빈 배열로 명시적으로 설정 (이미 기본값이지만 명확성을 위해)
                if hasattr(result, result_key):
                    setattr(result, result_key, [])

        # 4. 결과 출력
        print_weekly_recommendations(result, student_info)

        # 5. JSON 출력 (file_type을 첫 번째 키로 추가)
        result_dict = {"file_type": "weekly", **result.model_dump()}
        print("\nJSON 형식:")
        print(json.dumps(result_dict, ensure_ascii=False, indent=2))

        # 6. JSON 파일로 저장
        output_path = "weekly_content.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=2)
        print(f"\n{output_path} 파일로 저장 완료!")

    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()