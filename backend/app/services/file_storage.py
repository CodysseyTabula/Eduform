"""
JSON 파일 디스크 저장/로드 유틸리티

파일 경로 패턴: {STORAGE_PATH}/iep/{iep_version_id}/{file_type}-{ts}.json
"""

from __future__ import annotations

import json
import os
import tempfile
import time
from pathlib import Path
from typing import Any

from app.core.config import settings


class FileStorageError(Exception):
    """파일 저장/로드 관련 예외"""
    pass


def save_json_file(iep_version_id: str, file_type: str, content: dict) -> str:
    """
    JSON 파일을 디스크에 원자적으로 저장
    
    Args:
        iep_version_id: IEP 버전 ID (UUID)
        file_type: 파일 타입 ("student_info", "goal", "weekly_content", "weekly_material")
        content: JSON 컨텐츠 (dict)
    
    Returns:
        str: 저장된 파일의 절대 경로
    
    Raises:
        FileStorageError: 파일 저장 실패 시
    """
    try:
        # 디렉토리 구조 생성: {STORAGE_PATH}/iep/{iep_version_id}/
        version_dir = Path(settings.storage_path) / "iep" / str(iep_version_id)
        version_dir.mkdir(parents=True, exist_ok=True)
        
        # 파일 경로: {file_type}-{timestamp}.json
        timestamp = int(time.time())
        final_path = version_dir / f"{file_type}-{timestamp}.json"
        
        # 원자적 쓰기: 임시 파일에 먼저 쓰고 rename
        temp_fd, temp_path = tempfile.mkstemp(
            suffix=".json",
            dir=version_dir,
            text=True
        )
        
        try:
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                json.dump(content, f, ensure_ascii=False, indent=2)
            
            # 임시 파일을 최종 경로로 이동 (atomic)
            os.replace(temp_path, final_path)
            
            return str(final_path.absolute())
        
        except Exception:
            # 임시 파일 정리
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise
    
    except PermissionError as e:
        raise FileStorageError(f"Permission denied: {e}") from e
    except OSError as e:
        raise FileStorageError(f"File system error: {e}") from e
    except Exception as e:
        raise FileStorageError(f"Failed to save JSON file: {e}") from e


def load_json_file(file_path: str) -> dict[str, Any]:
    """
    디스크에서 JSON 파일 로드
    
    Args:
        file_path: 파일 경로
    
    Returns:
        dict: JSON 컨텐츠
    
    Raises:
        FileStorageError: 파일이 존재하지 않거나 JSON 파싱 실패 시
    """
    try:
        if not os.path.exists(file_path):
            raise FileStorageError(f"File not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = json.load(f)
        
        # JSON 객체 검증
        if not isinstance(content, dict):
            raise FileStorageError(
                f"Expected JSON object (dict), got {type(content).__name__}"
            )
        
        return content
    
    except json.JSONDecodeError as e:
        raise FileStorageError(f"Invalid JSON: {e}") from e
    except FileStorageError:
        raise
    except Exception as e:
        raise FileStorageError(f"Failed to load JSON file: {e}") from e


__all__ = ["save_json_file", "load_json_file", "FileStorageError"]
