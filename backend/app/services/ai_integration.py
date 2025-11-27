"""
AI 통합 서비스 레이어

현재는 사용되지 않습니다. 
IEP 파일 생성은 app/api/iep_files.py의 create_iep_file 엔드포인트를 통해
file_type별로 1개씩 생성됩니다.
"""

from __future__ import annotations


class AIIntegrationError(Exception):
    """AI 통합 관련 예외"""
    pass


__all__ = ["AIIntegrationError"]



