from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from pydantic import BaseModel
import dotenv
import os
import json
from typing import List, Dict, Optional


# 도메인 매핑 (recommend_weekly.py에서 참고)
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


# Pydantic 모델 정의
class WeeklyMaterialRecommendation(BaseModel):
    """단일 주차의 자료 추천 결과"""
    title: str
    reason: str
    content_url: str
    thumbnail_url: str


class SingleWeekMaterialResult(BaseModel):
    """단일 주차에 대한 자료 추천 결과"""
    recommendation: WeeklyMaterialRecommendation


class WeeklyMaterialResult(BaseModel):
    """전체 주차별 교육자료 추천 결과"""
    listeningSpeaking_weekly_material: List[WeeklyMaterialRecommendation] = []
    reading_weekly_material: List[WeeklyMaterialRecommendation] = []
    writing_weekly_material: List[WeeklyMaterialRecommendation] = []
    grammar_weekly_material: List[WeeklyMaterialRecommendation] = []
    literature_weekly_material: List[WeeklyMaterialRecommendation] = []
    mediaLiteracy_weekly_material: List[WeeklyMaterialRecommendation] = []
    numbersOperations_weekly_material: List[WeeklyMaterialRecommendation] = []
    changeAndRelations_weekly_material: List[WeeklyMaterialRecommendation] = []
    geometryMeasurement_weekly_material: List[WeeklyMaterialRecommendation] = []
    dataAndProbability_weekly_material: List[WeeklyMaterialRecommendation] = []


# 기존 recommend_materials.py의 유틸리티 함수 재사용
def setup_pinecone(api_key, index_name):
    """Pinecone 연결"""
    pc = Pinecone(api_key=api_key)
    return pc.Index(index_name)


def load_embedding_model(model_name):
    """임베딩 모델 로드"""
    return SentenceTransformer(model_name)


def setup_openai_client(api_key):
    """OpenAI 클라이언트 설정"""
    return OpenAI(api_key=api_key)


def search_materials(index, model, query, namespace, top_k=5):
    """과목별 자료 검색"""
    query_embedding = model.encode(query)
    
    results = index.query(
        vector=query_embedding.tolist(),
        top_k=top_k,
        include_metadata=True,
        namespace=namespace
    )
    
    return results


def load_weekly_content(file_path: str = "weekly_content.json") -> Dict:
    """주차별 학습 내용 JSON 파일 읽기"""
    with open(file_path, 'r', encoding='utf-8') as f:
        weekly_content = json.load(f)
    return weekly_content


def get_domain_info(key_base: str) -> tuple:
    """도메인 키 기반으로 과목과 namespace 반환"""
    # 국어 도메인 확인
    for domain_name, base in KOREAN_DOMAIN_MAPPING.items():
        if base == key_base:
            return ("korean", "korean")
    
    # 수학 도메인 확인
    for domain_name, base in MATH_DOMAIN_MAPPING.items():
        if base == key_base:
            return ("math", "math")
    
    return ("korean", "korean")  # 기본값


def create_material_recommendation_prompt(weekly_content: str, search_results: Dict) -> str:
    """주차별 학습 내용 기반 자료 추천 프롬프트 생성"""
    materials_text = ""
    for i, match in enumerate(search_results['matches'], 1):
        meta = match['metadata']
        materials_text += f"[자료 {i}]\n"
        materials_text += f"  제목: {meta.get('title', 'N/A')}\n"
        materials_text += f"  키워드: {meta.get('keywords', 'N/A')}\n"
        materials_text += f"  링크: {meta.get('content_url', 'N/A')}\n"
        materials_text += f"  썸네일: {meta.get('thumbnail_url', 'N/A')}\n\n"
    
    prompt = f"""
주차별 학습 내용: {weekly_content}

검색된 자료:
{materials_text}

위 자료 중 주차별 학습 내용에 가장 적합한 자료 1개를 선택하고, 추천 이유를 1문장으로 설명해주세요.
응답할 때 반드시 제목, 추천 이유, 링크(content_url), 썸네일(thumbnail_url)을 모두 포함해주세요.
"""
    return prompt


def recommend_material_for_week(
    client: OpenAI,
    weekly_content: str,
    search_results: Dict
) -> WeeklyMaterialRecommendation:
    """검색된 자료 중 AI가 가장 적합한 자료 선별"""
    
    if not search_results['matches']:
        # 검색 결과가 없을 경우 빈 추천 반환
        return WeeklyMaterialRecommendation(
            title="자료 없음",
            reason="해당 주차 학습 내용에 맞는 자료를 찾을 수 없습니다.",
            content_url="",
            thumbnail_url=""
        )
    
    prompt = create_material_recommendation_prompt(weekly_content, search_results)
    
    response = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[{"role": "user", "content": prompt}],
        response_format=SingleWeekMaterialResult
    )
    
    return response.choices[0].message.parsed.recommendation


def process_weekly_content_for_domain(
    index,
    embedding_model,
    openai_client,
    domain_key: str,
    weekly_content_list: List[str],
    namespace: str
) -> List[WeeklyMaterialRecommendation]:
    """특정 도메인의 모든 주차에 대해 자료 추천 수행"""
    recommendations = []
    
    print(f"  도메인 {domain_key} 처리 중...")
    
    for week_idx, weekly_content in enumerate(weekly_content_list, 1):
        # 주차 번호 제거 (예: "1주차: " 부분 제거)
        content_clean = weekly_content
        if ":" in weekly_content:
            content_clean = weekly_content.split(":", 1)[1].strip()
        
        if not content_clean:
            # 빈 내용인 경우 빈 추천 추가
            recommendations.append(WeeklyMaterialRecommendation(
                title="자료 없음",
                reason="해당 주차에 학습 내용이 없습니다.",
                content_url="",
                thumbnail_url=""
            ))
            continue
        
        try:
            # 1. Pinecone 검색
            search_results = search_materials(
                index,
                embedding_model,
                content_clean,
                namespace=namespace,
                top_k=5
            )
            
            # 2. AI 추천
            recommendation = recommend_material_for_week(
                openai_client,
                content_clean,
                search_results
            )
            
            recommendations.append(recommendation)
            
            if week_idx % 5 == 0:
                print(f"    {week_idx}주차 완료...")
        
        except Exception as e:
            print(f"    {week_idx}주차 처리 중 오류: {e}")
            # 오류 발생 시 빈 추천 추가
            recommendations.append(WeeklyMaterialRecommendation(
                title="처리 오류",
                reason=f"자료 추천 처리 중 오류가 발생했습니다: {str(e)}",
                content_url="",
                thumbnail_url=""
            ))
    
    return recommendations


def generate_weekly_materials(
    index,
    embedding_model,
    openai_client,
    weekly_content: Dict
) -> WeeklyMaterialResult:
    """모든 도메인과 주차에 대해 자료 추천 수행"""
    result = WeeklyMaterialResult()
    
    # 모든 도메인 키 정의
    all_domain_keys = [
        "listeningSpeaking",
        "reading",
        "writing",
        "grammar",
        "literature",
        "mediaLiteracy",
        "numbersOperations",
        "changeAndRelations",
        "geometryMeasurement",
        "dataAndProbability"
    ]
    
    for domain_key in all_domain_keys:
        content_key = f"{domain_key}_weeklyContent"
        material_key = f"{domain_key}_weekly_material"
        
        # 주차별 학습 내용 가져오기
        weekly_content_list = weekly_content.get(content_key, [])
        
        if not weekly_content_list:
            # 학습 내용이 없으면 빈 배열로 설정
            setattr(result, material_key, [])
            continue
        
        # 도메인 정보 가져오기 (과목, namespace)
        subject, namespace = get_domain_info(domain_key)
        
        # 주차별 자료 추천 수행
        recommendations = process_weekly_content_for_domain(
            index,
            embedding_model,
            openai_client,
            domain_key,
            weekly_content_list,
            namespace
        )
        
        # 결과 설정
        setattr(result, material_key, recommendations)
    
    return result


def print_weekly_material_recommendations(result: WeeklyMaterialResult):
    """주차별 교육자료 추천 결과 출력"""
    print("=" * 60)
    print("AI 주차별 교육자료 추천 결과")
    print("=" * 60)
    
    # 국어 도메인 출력
    korean_domains = [
        ("listeningSpeaking_weekly_material", "듣기말하기"),
        ("reading_weekly_material", "읽기"),
        ("writing_weekly_material", "쓰기"),
        ("grammar_weekly_material", "문법"),
        ("literature_weekly_material", "문학"),
        ("mediaLiteracy_weekly_material", "매체")
    ]
    
    print("\n[국어 영역]")
    for key, domain_name in korean_domains:
        materials = getattr(result, key, [])
        if materials:
            print(f"\n{domain_name}:")
            for week, material in enumerate(materials, 1):
                print(f"  {week}주차: {material.title}")
                print(f"    추천 이유: {material.reason}")
                print(f"    링크: {material.content_url}")
    
    # 수학 도메인 출력
    math_domains = [
        ("numbersOperations_weekly_material", "수와 연산"),
        ("changeAndRelations_weekly_material", "변화와 관계"),
        ("geometryMeasurement_weekly_material", "도형과 측정"),
        ("dataAndProbability_weekly_material", "자료와 가능성")
    ]
    
    print("\n[수학 영역]")
    for key, domain_name in math_domains:
        materials = getattr(result, key, [])
        if materials:
            print(f"\n{domain_name}:")
            for week, material in enumerate(materials, 1):
                print(f"  {week}주차: {material.title}")
                print(f"    추천 이유: {material.reason}")
                print(f"    링크: {material.content_url}")
    
    print("\n" + "=" * 60)


def main():
    # 환경 변수 로드
    dotenv.load_dotenv()
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not pinecone_api_key or not openai_api_key:
        print("오류: API 키가 설정되지 않았습니다.")
        print("PINECONE_API_KEY와 OPENAI_API_KEY 환경 변수를 설정해주세요.")
        return
    
    # 서비스 초기화
    print("=" * 60)
    print("AI 기반 주차별 교육자료 추천")
    print("=" * 60)
    print("\n서비스 초기화 중...")
    
    index = setup_pinecone(pinecone_api_key, "integrated-dense-py")
    embedding_model = load_embedding_model('jhgan/ko-sroberta-multitask')
    openai_client = setup_openai_client(openai_api_key)
    
    print("초기화 완료!\n")
    
    try:
        # 1. 주차별 학습 내용 읽기
        weekly_content_path = "weekly_content.json"
        print(f"주차별 학습 내용 파일 읽기: {weekly_content_path}")
        weekly_content = load_weekly_content(weekly_content_path)
        print("파일 읽기 완료!\n")
        
        # 2. 모든 도메인과 주차에 대해 자료 추천 수행
        print("주차별 교육자료 추천 시작...")
        result = generate_weekly_materials(
            index,
            embedding_model,
            openai_client,
            weekly_content
        )
        print("\n모든 추천 완료!\n")
        
        # 3. 결과 출력
        print_weekly_material_recommendations(result)
        
        # 4. JSON 출력
        print("\nJSON 형식:")
        output_data = {"file_type": "material", **result.model_dump()}
        print(json.dumps(output_data, ensure_ascii=False, indent=2))
        
        # 5. JSON 파일로 저장
        output_path = "weekly_material_recommendations.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        print(f"\n{output_path} 파일로 저장 완료!")
    
    except FileNotFoundError as e:
        print(f"\n오류: 파일을 찾을 수 없습니다. {e}")
        print(f"다음 파일이 필요합니다: weekly_content.json")
    except json.JSONDecodeError as e:
        print(f"\n오류: JSON 파일 파싱 실패. {e}")
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
