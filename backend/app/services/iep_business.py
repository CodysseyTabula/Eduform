"""
IEP 비즈니스 로직 서비스

- 연간 목표 상속 (2학기 → 1학기 annual_*_goal 복사)
- 파일 저장/업데이트 통합 (덮어쓰기 로직)
- IEP 완료 검증 (3개 파일 존재 확인)
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy.orm import Session

from app.models.iep_file import IEPFile
from app.models.iep_version import IEPVersion
from app.services.file_storage import load_json_file, save_json_file

if TYPE_CHECKING:
    from typing import Any


class IEPBusinessError(Exception):
    """IEP 비즈니스 로직 관련 예외"""
    pass


def inherit_annual_goals(
    db: Session,
    from_iep_version_id: uuid.UUID,
    to_iep_version_id: uuid.UUID
) -> None:
    """
    연간 목표 강제 상속 (1학기 → 2학기)
    
    1학기 IEP의 goals.json에서 annual_*_goal 필드들을 읽어
    2학기 IEP의 goals.json에 복사 (무조건 덮어쓰기)
    
    Args:
        db: 데이터베이스 세션
        from_iep_version_id: 원본 IEP 버전 ID (보통 1학기)
        to_iep_version_id: 대상 IEP 버전 ID (보통 2학기)
    
    Raises:
        IEPBusinessError: IEP 버전이 없거나 goals 파일이 없을 때
    """
    try:
        # 1. 원본 IEP 버전 확인
        from_version = db.query(IEPVersion).filter(
            IEPVersion.id == from_iep_version_id
        ).first()
        
        if not from_version:
            raise IEPBusinessError(
                f"Source IEP version not found: {from_iep_version_id}"
            )
        
        # 2. 대상 IEP 버전 확인
        to_version = db.query(IEPVersion).filter(
            IEPVersion.id == to_iep_version_id
        ).first()
        
        if not to_version:
            raise IEPBusinessError(
                f"Target IEP version not found: {to_iep_version_id}"
            )
        
        # 3. 원본 goals.json 파일 찾기
        from_goals_file = db.query(IEPFile).filter(
            IEPFile.iep_version_id == from_iep_version_id,
            IEPFile.file_type == "goal"
        ).first()
        
        if not from_goals_file:
            raise IEPBusinessError(
                f"Goals file not found for source IEP version: {from_iep_version_id}"
            )
        
        # 4. 원본 goals.json 로드
        from_goals_content = load_json_file(from_goals_file.file_path)
        
        # 5. 대상 goals.json 파일 찾기 (없으면 나중에 생성)
        to_goals_file = db.query(IEPFile).filter(
            IEPFile.iep_version_id == to_iep_version_id,
            IEPFile.file_type == "goal"
        ).first()
        
        # 6. 대상 goals 내용 준비
        if to_goals_file:
            # 기존 파일이 있으면 로드
            to_goals_content = load_json_file(to_goals_file.file_path)
        else:
            # 없으면 빈 딕셔너리로 시작
            to_goals_content = {}
        
        # 7. annual_*_goal 필드들만 추출하여 복사
        annual_goals = {
            key: value
            for key, value in from_goals_content.items()
            if key.startswith("annual_")
        }
        
        if not annual_goals:
            raise IEPBusinessError(
                f"No annual goals found in source IEP version: {from_iep_version_id}"
            )
        
        # 8. 대상에 annual 목표 덮어쓰기
        to_goals_content.update(annual_goals)
        
        # 9. 대상 goals.json 저장 (save_or_update_iep_file 사용)
        save_or_update_iep_file(
            db=db,
            iep_version_id=to_iep_version_id,
            file_type="goal",
            content=to_goals_content
        )
        
        db.commit()
    
    except IEPBusinessError:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise IEPBusinessError(
            f"Failed to inherit annual goals: {e}"
        ) from e


def save_or_update_iep_file(
    db: Session,
    iep_version_id: uuid.UUID,
    file_type: str,
    content: dict[str, Any]
) -> IEPFile:
    """
    IEP 파일 저장 또는 업데이트 (덮어쓰기)
    
    같은 iep_version_id + file_type 조합이 존재하면:
    - 새 파일을 디스크에 생성
    - 기존 DB 레코드의 file_path를 새 경로로 업데이트
    - updated_at 갱신
    
    존재하지 않으면:
    - 새 파일을 디스크에 생성
    - 새 DB 레코드 생성
    
    Args:
        db: 데이터베이스 세션
        iep_version_id: IEP 버전 ID
        file_type: 파일 타입 ("goal", "weekly_plan", "material")
        content: JSON 컨텐츠
    
    Returns:
        IEPFile: 생성/업데이트된 IEPFile 모델 인스턴스
    
    Raises:
        IEPBusinessError: IEP 버전이 없거나 파일 저장 실패 시
    """
    try:
        # 1. IEP 버전 존재 확인
        iep_version = db.query(IEPVersion).filter(
            IEPVersion.id == iep_version_id
        ).first()
        
        if not iep_version:
            raise IEPBusinessError(
                f"IEP version not found: {iep_version_id}"
            )
        
        # 2. 파일 타입 검증
        valid_file_types = ["goal", "weekly_plan", "material"]
        if file_type not in valid_file_types:
            raise IEPBusinessError(
                f"Invalid file_type: {file_type}. Must be one of {valid_file_types}"
            )
        
        # 3. 디스크에 JSON 파일 저장 (새 파일 생성)
        file_path = save_json_file(
            iep_version_id=str(iep_version_id),
            file_type=file_type,
            content=content
        )
        
        # 4. 기존 파일 레코드 확인
        existing_file = db.query(IEPFile).filter(
            IEPFile.iep_version_id == iep_version_id,
            IEPFile.file_type == file_type
        ).first()
        
        if existing_file:
            # 5a. 기존 레코드 업데이트 (file_path, updated_at)
            existing_file.file_path = file_path
            # updated_at은 onupdate=datetime.utcnow로 자동 갱신됨
            db.flush()  # DB에 반영 (커밋 전)
            return existing_file
        else:
            # 5b. 새 레코드 생성
            new_file = IEPFile(
                iep_version_id=iep_version_id,
                file_type=file_type,
                file_path=file_path
            )
            db.add(new_file)
            db.flush()  # DB에 반영 (커밋 전)
            return new_file
    
    except IEPBusinessError:
        raise
    except Exception as e:
        raise IEPBusinessError(
            f"Failed to save/update IEP file: {e}"
        ) from e


def verify_iep_complete(
    db: Session,
    iep_version_id: uuid.UUID
) -> bool:
    """
    IEP 완료 검증 (3개 파일 모두 존재해야 완료)
    
    다음 파일들이 모두 존재하는지 확인:
    - goals
    - weekly_plan
    - weekly_materials
    
    Args:
        db: 데이터베이스 세션
        iep_version_id: IEP 버전 ID
    
    Returns:
        bool: 3개 파일 모두 존재하면 True, 아니면 False
    
    Raises:
        IEPBusinessError: IEP 버전이 존재하지 않을 때
    """
    try:
        # 1. IEP 버전 존재 확인
        iep_version = db.query(IEPVersion).filter(
            IEPVersion.id == iep_version_id
        ).first()
        
        if not iep_version:
            raise IEPBusinessError(
                f"IEP version not found: {iep_version_id}"
            )
        
        # 2. 필수 파일 타입 목록
        required_file_types = ["goal", "weekly_plan", "material"]
        
        # 3. 각 파일 타입별로 존재 확인
        for file_type in required_file_types:
            file_exists = db.query(IEPFile).filter(
                IEPFile.iep_version_id == iep_version_id,
                IEPFile.file_type == file_type
            ).first()
            
            if not file_exists:
                return False
        
        # 4. 모든 파일이 존재하면 True
        return True
    
    except IEPBusinessError:
        raise
    except Exception as e:
        raise IEPBusinessError(
            f"Failed to verify IEP completion: {e}"
        ) from e


__all__ = [
    "inherit_annual_goals",
    "save_or_update_iep_file",
    "verify_iep_complete",
    "IEPBusinessError",
]



