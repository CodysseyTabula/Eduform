"""
IEP 파일 생성/수정 API 라우터
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import UUID

import os
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from ai_module.pipeline import generate_goal_file_content, generate_weekly_content_file
from app.db.session import get_db
from app.models.iep_file import IEPFile
from app.models.iep_version import IEPVersion
from app.schemas.iep_file import IEPFileResponse
from app.schemas.student_profile import StudentProfile
from app.services.file_storage import save_json_file, FileStorageError

router = APIRouter(prefix="/iep-files", tags=["IEP Files"])


def _normalize_weekly_content_shape(raw_weekly: dict) -> dict:
    """
    weekly_content 데이터를 일관된 스키마({domain}_weeklyContent: [str, ...])로 변환.
    - 입력이 {domain: [{week, content}, ...]} 형태여도 처리
    - 입력이 이미 *_weeklyContent 리스트 형태면 그대로 사용
    """
    if not isinstance(raw_weekly, dict):
        return {}
    
    normalized = {"file_type": "weekly"}
    
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
        "dataAndProbability",
    ]
    
    for domain_key in all_domain_keys:
        legacy_key = f"{domain_key}_weeklyContent"
        # 1) 우선 *_weeklyContent 키 우선 사용
        content_list = raw_weekly.get(legacy_key)
        # 2) 없다면 도메인 키 자체가 있을 수 있음 (LLM 출력 형태)
        if content_list is None and domain_key in raw_weekly:
            content_list = raw_weekly.get(domain_key)
        
        if not content_list:
            normalized[legacy_key] = []
            continue
        
        # 리스트 형태만 인정
        if isinstance(content_list, list):
            normalized_list = []
            for item in content_list:
                if isinstance(item, dict):
                    # {week, content} 형태일 때 content만 추출
                    content = item.get("content") or ""
                    if content is not None:
                        normalized_list.append(str(content).strip())
                elif isinstance(item, str):
                    normalized_list.append(item.strip())
            normalized[legacy_key] = normalized_list
        else:
            # 리스트가 아니면 빈 리스트로 처리
            normalized[legacy_key] = []
    
    return normalized


@router.post("", response_model=IEPFileResponse, status_code=status.HTTP_201_CREATED)
async def create_iep_file(
    iep_version_id: str = Form(..., description="IEP 버전 ID (UUID)"),
    file_type: str = Form(..., description="파일 타입 (student_info, goal, weekly_content, weekly_material)"),
    file: UploadFile = File(..., description="학생 프로필 JSON 파일 (20개 필드)"),
    db: Session = Depends(get_db),
) -> IEPFileResponse:
    """
    IEP 파일 생성 (AI 모듈 사용)
    
    사용자가 file_type을 선택하여 해당 타입의 IEP 파일 1개를 생성합니다.
    4개 파일(student_info, goal, weekly_content, weekly_material)을 모두 만들려면 이 API를 호출해야 합니다.
    
    **프로세스:**
    1. multipart/form-data로 student_profile JSON 파일 수신
    2. IEP Version 존재 여부 검증
    3. file_type에 따라 recommend_* 모듈 호출
       - "student_info" → 업로드된 프로필을 그대로 저장
       - "goal" → ai_module.recommend_goal 기반 목표 생성
       - "weekly_content" → ai_module.recommend_weekly 기반 학습 내용 생성
       - "weekly_material" → ai_module.recommend_weekly_material 기반 자료 추천
    4. 생성된 JSON을 디스크에 저장
    5. IEP_FILE 레코드 DB에 저장
    
    **요청 (multipart/form-data):**
    - **iep_version_id**: IEP 버전 ID (UUID)
    - **file_type**: "student_info", "goal", "weekly_content", "weekly_material" 중 하나 선택
    - **file**: 학생 프로필 JSON 파일 (20개 필드)
    
    **응답:**
    - 생성된 IEP 파일 메타데이터 (단일 객체)
    
    **에러 응답:**
    - 400: JSON 형식 오류, Validation 실패, 잘못된 file_type
    - 404: IEP version not found
    - 500: AI 모듈 호출 실패 또는 파일 저장 실패
    """
    # 1. UUID 파싱
    try:
        iep_version_uuid = UUID(iep_version_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID format for iep_version_id"
        )
    
    # 2. file_type 검증
    valid_file_types = ["student_info", "goal", "weekly_content", "weekly_material"]
    if file_type not in valid_file_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file_type. Must be one of: {', '.join(valid_file_types)}"
        )
    
    # 3. IEP Version 존재 검증
    iep_version = db.query(IEPVersion).filter(
        IEPVersion.id == iep_version_uuid
    ).first()
    
    if not iep_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="IEP version not found"
        )
    
    # 4. 업로드된 JSON 파일 읽기 및 파싱
    try:
        content = await file.read()
        uploaded_data = json.loads(content.decode('utf-8'))
        
        # 디버깅: 파일 타입별로 받은 데이터 확인
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"파일 타입: {file_type}, 파일명: {file.filename}")
        logger.info(f"받은 데이터 키: {list(uploaded_data.keys()) if isinstance(uploaded_data, dict) else 'not a dict'}")
        if file_type == "weekly_material":
            logger.info(f"weekly_content 데이터 전체: {uploaded_data}")
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON file format: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read uploaded file: {str(e)}"
        )
    
    # 5. file_type에 따라 처리
    try:
        if file_type == "weekly_material":
            # weekly_material 타입일 때는 업로드된 파일이 weekly_content 형식
            import dotenv
            from ai_module import recommend_weekly_material as rwm
            
            # 환경 변수 로드
            dotenv.load_dotenv()
            pinecone_api_key = os.getenv("PINECONE_API_KEY")
            openai_api_key = os.getenv("OPENAI_API_KEY")
            
            if not pinecone_api_key or not openai_api_key:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="PINECONE_API_KEY와 OPENAI_API_KEY 환경 변수가 필요합니다."
                )
            
            # weekly_content 데이터 (업로드된 파일)
            weekly_content = uploaded_data
            
            # 디버깅: 받은 데이터 확인
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"받은 weekly_content 데이터 키: {list(weekly_content.keys())}")
            logger.info(f"받은 weekly_content 데이터: {weekly_content}")
            
            # 주차별 학습 내용 정보 로깅 (검증 없이 유연하게 처리)
            content_summary = []
            for key in weekly_content.keys():
                if key.endswith("_weeklyContent"):
                    content_list = weekly_content.get(key, [])
                    is_list = isinstance(content_list, list)
                    length = len(content_list) if is_list else 0
                    content_summary.append({
                        "key": key,
                        "length": length,
                        "has_content": length > 0
                    })
            
            logger.info(f"weekly_content 요약: {content_summary}")
            logger.info("검증 없이 유연하게 처리합니다. 빈 배열이 있는 도메인은 자동으로 건너뜁니다.")
            
            # 서비스 초기화
            logger.info("Pinecone, Embedding 모델, OpenAI 클라이언트 초기화 중...")
            try:
                index = rwm.setup_pinecone(pinecone_api_key, "integrated-dense-py")
                logger.info("Pinecone 인덱스 연결 완료")
            except Exception as e:
                logger.error(f"Pinecone 초기화 실패: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Pinecone 초기화 실패: {str(e)}"
                )
            
            try:
                embedding_model = rwm.load_embedding_model('jhgan/ko-sroberta-multitask')
                logger.info("Embedding 모델 로드 완료")
            except Exception as e:
                logger.error(f"Embedding 모델 로드 실패: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Embedding 모델 로드 실패: {str(e)}"
                )
            
            try:
                openai_client = rwm.setup_openai_client(openai_api_key)
                logger.info("OpenAI 클라이언트 초기화 완료")
            except Exception as e:
                logger.error(f"OpenAI 클라이언트 초기화 실패: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"OpenAI 클라이언트 초기화 실패: {str(e)}"
                )
            
            # 주차별 교육자료 추천 수행
            logger.info("generate_weekly_materials 함수 호출 시작...")
            logger.info(f"전달되는 weekly_content 키: {list(weekly_content.keys())}")
            
            try:
                weekly_content = _normalize_weekly_content_shape(weekly_content)
                result = rwm.generate_weekly_materials(
                    index,
                    embedding_model,
                    openai_client,
                    weekly_content
                )
                logger.info("generate_weekly_materials 함수 호출 완료")
                logger.info(f"결과 타입: {type(result)}")
                result_dict = result.model_dump()
                logger.info(f"결과 키: {list(result_dict.keys())}")
                for key, value in result_dict.items():
                    if isinstance(value, list):
                        logger.info(f"  {key}: {len(value)}개 항목")
                    else:
                        logger.info(f"  {key}: {type(value)}")
            except Exception as e:
                logger.error(f"generate_weekly_materials 실행 중 오류 발생: {e}")
                import traceback
                logger.error(f"상세 오류: {traceback.format_exc()}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"주차별 교육자료 추천 중 오류 발생: {str(e)}"
                )
            
            # Pydantic 모델을 dict로 변환하고 스펙에 맞는 형식으로 변환
            # 현재 형식: {domain_weekly_material: [{title, reason, content_url, thumbnail_url}, ...]}
            # 스펙 형식: {domain_weekly_material: [{week: number, materials: [{title, url, keywords, file_type}]}, ...]}
            if result is None:
                logger.error("generate_weekly_materials가 None을 반환했습니다.")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="주차별 교육자료 추천 결과가 없습니다."
                )
            
            result_dict = result.model_dump()
            logger.info(f"변환된 result_dict 키: {list(result_dict.keys())}")
            generated_data = {"file_type": "material"}
            
            for domain_key, materials_list in result_dict.items():
                if domain_key.endswith("_weekly_material"):
                    if not isinstance(materials_list, list):
                        raise HTTPException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"{domain_key}의 데이터 형식이 올바르지 않습니다. list가 아닙니다."
                        )
                    
                    # 주차별로 변환 (1주차부터 시작)
                    converted_list = []
                    for week_idx, material in enumerate(materials_list, 1):
                        if not isinstance(material, dict):
                            raise HTTPException(
                                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"{domain_key}의 {week_idx}주차 데이터 형식이 올바르지 않습니다. dict가 아닙니다."
                            )
                        
                        # 필수 필드 확인
                        if "content_url" not in material and "url" not in material:
                            raise HTTPException(
                                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"{domain_key}의 {week_idx}주차 데이터에 content_url 또는 url이 없습니다."
                            )
                        
                        # title 추출 (여러 가능한 키 확인)
                        title = material.get("title", "") or material.get("name", "") or ""
                        title = title.strip() if title else ""
                        
                        # URL 추출
                        url = material.get("content_url", "") or material.get("url", "")
                        
                        # 썸네일 URL 추출
                        thumbnail_url = material.get("thumbnail_url", "") or ""
                        
                        # 디버깅 로그
                        logger.info(f"{domain_key} {week_idx}주차 - title: '{title}', url: '{url[:50] if url else '없음'}...', thumbnail: '{thumbnail_url[:50] if thumbnail_url else '없음'}...'")
                        
                        # 스펙에 맞는 형식으로 변환
                        # MaterialItem: {title, url, keywords, file_type, thumbnail_url}
                        # WeekMaterialItem: {week, materials: [MaterialItem]}
                        converted_item = {
                            "week": week_idx,
                            "materials": [{
                                "title": title,
                                "url": url,  # content_url → url 변환
                                "keywords": "",  # keywords는 현재 AI 모듈에서 제공하지 않으므로 빈 문자열
                                "file_type": "",  # file_type도 현재 AI 모듈에서 제공하지 않으므로 빈 문자열
                                "thumbnail_url": thumbnail_url  # 썸네일 URL 포함
                            }]
                        }
                        converted_list.append(converted_item)
                    generated_data[domain_key] = converted_list
            
            # 스키마 검증 - 실패 시 에러 발생
            from app.schemas.iep_file import WeeklyMaterialsContent
            try:
                validated_data = WeeklyMaterialsContent(**generated_data)
                # 검증 통과 시 dict로 변환하여 사용
                generated_data = validated_data.model_dump(exclude_none=True)
            except Exception as e:
                # 스키마 검증 실패 시 에러 발생 (임시 방편 없이)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"WeeklyMaterialsContent 스키마 검증 실패: {str(e)}"
                )
            
        else:
            # 다른 타입들은 기존 로직 사용
            # StudentProfile 스키마 검증
            try:
                student_profile = StudentProfile(**uploaded_data)
                profile_dict = student_profile.model_dump()
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid student profile data: {str(e)}"
                )

            if file_type == "student_info":
                generated_data = profile_dict
            elif file_type == "goal":
                generated_data = generate_goal_file_content(profile_dict)
            elif file_type == "weekly_content":
                weekly_content = generate_weekly_content_file(profile_dict)
                generated_data = _normalize_weekly_content_shape(weekly_content)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI module error: {str(e)}"
        )
    
    # 7. 디스크에 파일 저장
    try:
        file_path = save_json_file(
            str(iep_version_uuid),
            file_type,
            generated_data
        )
    except FileStorageError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # 8. DB에 메타데이터 저장
    try:
        iep_file = IEPFile(
            iep_version_id=iep_version_uuid,
            file_type=file_type,
            file_path=file_path
        )
        
        db.add(iep_file)
        db.commit()
        db.refresh(iep_file)
        
        # file_content 포함 응답
        return IEPFileResponse(
            id=iep_file.id,
            iep_version_id=iep_file.iep_version_id,
            file_type=iep_file.file_type,
            file_path=iep_file.file_path,
            file_content=generated_data,
            updated_at=iep_file.updated_at,
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.put("/{file_id}", response_model=IEPFileResponse)
async def update_iep_file(
    file_id: UUID,
    file: UploadFile = File(..., description="업데이트할 JSON 파일"),
    db: Session = Depends(get_db),
) -> IEPFileResponse:
    """
    IEP 파일 업데이트
    
    기존 JSON 파일을 덮어쓰기합니다.
    - 새 파일을 타임스탬프와 함께 저장
    - IEPFile 레코드의 file_path 갱신
    - updated_at 자동 갱신
    
    **프로세스:**
    1. 기존 IEP 파일 레코드 조회
    2. 업로드된 파일 검증 (JSON 형식)
    3. 새 파일을 디스크에 저장 (새 타임스탬프)
    4. DB의 file_path와 updated_at 갱신
    
    **요청 (multipart/form-data):**
    - **file**: 업데이트할 JSON 파일 (.json)
    
    **응답:**
    - 업데이트된 IEP 파일 메타데이터
    
    **에러 응답:**
    - 400: JSON 파일 형식 오류
    - 404: IEP file not found
    - 500: 파일 저장 실패
    """
    # 1. 기존 파일 레코드 조회
    iep_file = db.query(IEPFile).filter(IEPFile.id == file_id).first()
    
    if not iep_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="IEP file not found"
        )
    
    # 2. 업로드된 파일 읽기 및 JSON 검증
    try:
        content = await file.read()
        json_data = json.loads(content.decode('utf-8'))
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON file format"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read uploaded file: {str(e)}"
        )
    
    # 3. 새 파일 저장 (타임스탬프 변경으로 새 파일명)
    try:
        new_file_path = save_json_file(
            str(iep_file.iep_version_id),
            iep_file.file_type,
            json_data
        )
    except FileStorageError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # 4. DB 업데이트
    try:
        iep_file.file_path = new_file_path
        iep_file.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(iep_file)
        
        # file_content 포함 응답
        return IEPFileResponse(
            id=iep_file.id,
            iep_version_id=iep_file.iep_version_id,
            file_type=iep_file.file_type,
            file_path=iep_file.file_path,
            file_content=json_data,
            updated_at=iep_file.updated_at,
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update database: {str(e)}"
        )
