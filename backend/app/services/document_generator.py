"""
IEP DOCX 문서 생성 서비스

IEP JSON 파일(goals, weekly_plan, weekly_materials)을 읽어
DOCX 문서를 생성하고 다운로드를 제공합니다.
"""

from __future__ import annotations

import os
import time
from io import BytesIO
from pathlib import Path
from typing import Any
from uuid import UUID

from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.iep_file import IEPFile
from app.models.iep_version import IEPVersion
from app.services.file_storage import load_json_file, FileStorageError


# ==================== 예외 정의 ====================

class DocumentGenerationError(Exception):
    """문서 생성 관련 기본 예외"""
    pass


class DocumentNotFoundError(DocumentGenerationError):
    """필요한 IEP 파일을 찾을 수 없을 때"""
    pass


class InvalidDocumentDataError(DocumentGenerationError):
    """JSON 데이터가 유효하지 않을 때"""
    pass


# ==================== 핵심 함수 ====================

def generate_docx_for_iep(
    db: Session,
    iep_version_id: UUID,
    output_path: str | None = None
) -> str:
    """
    IEP DOCX 파일 생성
    
    Args:
        db: 데이터베이스 세션
        iep_version_id: IEP 버전 ID (UUID)
        output_path: 저장할 파일 경로 (없으면 자동 생성)
    
    Returns:
        str: 생성된 DOCX 파일의 절대 경로
    
    Raises:
        DocumentNotFoundError: IEP 버전이나 필수 파일이 없을 때
        InvalidDocumentDataError: JSON 데이터가 유효하지 않을 때
        DocumentGenerationError: 기타 문서 생성 오류
    """
    try:
        # 1. IEP 버전 조회
        iep_version = db.query(IEPVersion).filter(
            IEPVersion.id == iep_version_id
        ).first()
        
        if not iep_version:
            raise DocumentNotFoundError(
                f"IEP version not found: {iep_version_id}"
            )
        
        # 2. IEP 파일 메타데이터 조회 (3개 파일 필요)
        iep_files = db.query(IEPFile).filter(
            IEPFile.iep_version_id == iep_version_id
        ).all()
        
        file_map = {f.file_type: f.file_path for f in iep_files}
        
        # 필수 파일 확인
        required_types = ["goals", "weekly_plan", "weekly_materials"]
        missing_types = [ft for ft in required_types if ft not in file_map]
        
        if missing_types:
            raise DocumentNotFoundError(
                f"Missing required IEP files: {', '.join(missing_types)}"
            )
        
        # 3. JSON 파일 로드
        try:
            goals_data = load_json_file(file_map["goals"])
            weekly_plan_data = load_json_file(file_map["weekly_plan"])
            weekly_materials_data = load_json_file(file_map["weekly_materials"])
        except FileStorageError as e:
            raise DocumentNotFoundError(f"Failed to load IEP JSON files: {e}") from e
        
        # 4. DOCX 문서 생성
        doc = Document()
        
        # 문서 제목
        title = doc.add_heading('개별화 교육 계획 (IEP)', level=1)
        title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        
        # IEP 메타데이터 섹션
        _add_metadata_section(doc, iep_version)
        
        # 연간/학기 목표 섹션
        _add_goals_section(doc, goals_data)
        
        # 주차별 학습 계획 섹션
        _add_weekly_plan_section(doc, weekly_plan_data)
        
        # 주차별 학습 자료 섹션
        _add_weekly_materials_section(doc, weekly_materials_data)
        
        # 5. 파일 저장
        if not output_path:
            # 자동 경로 생성: {STORAGE_PATH}/iep/{iep_version_id}/iep-{ts}.docx
            version_dir = Path(settings.storage_path) / "iep" / str(iep_version_id)
            version_dir.mkdir(parents=True, exist_ok=True)
            timestamp = int(time.time())
            output_path = str(version_dir / f"iep-{timestamp}.docx")
        
        doc.save(output_path)
        
        return str(Path(output_path).absolute())
    
    except (DocumentNotFoundError, InvalidDocumentDataError):
        raise
    except Exception as e:
        raise DocumentGenerationError(f"Failed to generate DOCX: {e}") from e


def generate_docx_stream(db: Session, iep_version_id: UUID) -> BytesIO:
    """
    IEP DOCX 파일을 메모리 스트림으로 생성 (다운로드용)
    
    Args:
        db: 데이터베이스 세션
        iep_version_id: IEP 버전 ID (UUID)
    
    Returns:
        BytesIO: DOCX 파일 바이너리 스트림
    
    Raises:
        DocumentNotFoundError, InvalidDocumentDataError, DocumentGenerationError
    """
    try:
        # 1. IEP 버전 조회
        iep_version = db.query(IEPVersion).filter(
            IEPVersion.id == iep_version_id
        ).first()
        
        if not iep_version:
            raise DocumentNotFoundError(
                f"IEP version not found: {iep_version_id}"
            )
        
        # 2. IEP 파일 메타데이터 조회
        iep_files = db.query(IEPFile).filter(
            IEPFile.iep_version_id == iep_version_id
        ).all()
        
        file_map = {f.file_type: f.file_path for f in iep_files}
        
        # 필수 파일 확인
        required_types = ["goals", "weekly_plan", "weekly_materials"]
        missing_types = [ft for ft in required_types if ft not in file_map]
        
        if missing_types:
            raise DocumentNotFoundError(
                f"Missing required IEP files: {', '.join(missing_types)}"
            )
        
        # 3. JSON 파일 로드
        try:
            goals_data = load_json_file(file_map["goals"])
            weekly_plan_data = load_json_file(file_map["weekly_plan"])
            weekly_materials_data = load_json_file(file_map["weekly_materials"])
        except FileStorageError as e:
            raise DocumentNotFoundError(f"Failed to load IEP JSON files: {e}") from e
        
        # 4. DOCX 문서 생성
        doc = Document()
        
        # 문서 제목
        title = doc.add_heading('개별화 교육 계획 (IEP)', level=1)
        title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        
        # IEP 메타데이터 섹션
        _add_metadata_section(doc, iep_version)
        
        # 연간/학기 목표 섹션
        _add_goals_section(doc, goals_data)
        
        # 주차별 학습 계획 섹션
        _add_weekly_plan_section(doc, weekly_plan_data)
        
        # 주차별 학습 자료 섹션
        _add_weekly_materials_section(doc, weekly_materials_data)
        
        # 5. 메모리 스트림에 저장
        stream = BytesIO()
        doc.save(stream)
        stream.seek(0)
        
        return stream
    
    except (DocumentNotFoundError, InvalidDocumentDataError):
        raise
    except Exception as e:
        raise DocumentGenerationError(f"Failed to generate DOCX stream: {e}") from e


# ==================== 내부 헬퍼 함수 ====================

def _add_metadata_section(doc: Document, iep_version: IEPVersion) -> None:
    """IEP 메타데이터 섹션 추가"""
    doc.add_heading('IEP 정보', level=2)
    
    # 메타데이터를 단락으로 출력 (테스트에서 paragraphs로 추출 가능하도록)
    doc.add_paragraph(f"학년도: {iep_version.year}", style='List Bullet')
    doc.add_paragraph(f"학기: {iep_version.semester}", style='List Bullet')
    doc.add_paragraph(f"학년: {iep_version.grade}", style='List Bullet')
    doc.add_paragraph(f"생성일: {iep_version.created_at.strftime('%Y-%m-%d %H:%M:%S')}", style='List Bullet')
    
    doc.add_paragraph()  # 간격


def _add_goals_section(doc: Document, goals_data: dict[str, Any]) -> None:
    """연간/학기 목표 섹션 추가"""
    doc.add_heading('1. 교육 목표', level=2)
    
    # 도메인 한글 매핑
    domain_names = {
        # 국어 도메인
        "listeningSpeaking": "국어 - 듣기말하기",
        "reading": "국어 - 읽기",
        "writing": "국어 - 쓰기",
        "grammar": "국어 - 문법",
        "literature": "국어 - 문학",
        "mediaLiteracy": "국어 - 매체",
        # 수학 도메인
        "numbersOperations": "수학 - 수와 연산",
        "changeAndRelations": "수학 - 변화와 관계",
        "geometryMeasurement": "수학 - 도형과 측정",
        "dataAndProbability": "수학 - 자료와 가능성",
    }
    
    # 선택된 도메인만 출력
    for domain_key, domain_name in domain_names.items():
        if domain_key in goals_data:
            domain_goals = goals_data[domain_key]
            
            # 도메인별 소제목
            doc.add_heading(domain_name, level=3)
            
            # 연간 목표
            if isinstance(domain_goals, dict) and "annual_goal" in domain_goals:
                doc.add_paragraph(
                    f"📌 연간 목표: {domain_goals['annual_goal']}",
                    style='List Bullet'
                )
            
            # 학기 목표
            if isinstance(domain_goals, dict) and "semester_goal" in domain_goals:
                doc.add_paragraph(
                    f"🎯 학기 목표: {domain_goals['semester_goal']}",
                    style='List Bullet'
                )
            
            doc.add_paragraph()  # 간격
    
    if not any(key in goals_data for key in domain_names.keys()):
        doc.add_paragraph("⚠️ 목표 데이터가 없습니다.", style='Intense Quote')


def _add_weekly_plan_section(doc: Document, weekly_plan_data: dict[str, Any]) -> None:
    """주차별 학습 계획 섹션 추가"""
    doc.add_heading('2. 주차별 학습 계획 (20주)', level=2)
    
    # 도메인 한글 매핑
    domain_names = {
        "listeningSpeaking": "국어 - 듣기말하기",
        "reading": "국어 - 읽기",
        "writing": "국어 - 쓰기",
        "grammar": "국어 - 문법",
        "literature": "국어 - 문학",
        "mediaLiteracy": "국어 - 매체",
        "numbersOperations": "수학 - 수와 연산",
        "changeAndRelations": "수학 - 변화와 관계",
        "geometryMeasurement": "수학 - 도형과 측정",
        "dataAndProbability": "수학 - 자료와 가능성",
    }
    
    # 선택된 도메인만 출력
    for domain_key, domain_name in domain_names.items():
        if domain_key in weekly_plan_data:
            weekly_content = weekly_plan_data[domain_key]
            
            # 도메인별 소제목
            doc.add_heading(domain_name, level=3)
            
            # 주차별 내용 출력
            if isinstance(weekly_content, list):
                for item in weekly_content:
                    if isinstance(item, dict):
                        week = item.get('week', '?')
                        content = item.get('content', '내용 없음')
                        doc.add_paragraph(
                            f"[{week}주차] {content}",
                            style='List Number'
                        )
            
            doc.add_paragraph()  # 간격
    
    if not any(key in weekly_plan_data for key in domain_names.keys()):
        doc.add_paragraph("⚠️ 주차별 학습 계획 데이터가 없습니다.", style='Intense Quote')


def _add_weekly_materials_section(doc: Document, weekly_materials_data: dict[str, Any]) -> None:
    """주차별 학습 자료 섹션 추가"""
    doc.add_heading('3. 주차별 학습 자료', level=2)
    
    # 도메인 한글 매핑
    domain_names = {
        "listeningSpeaking": "국어 - 듣기말하기",
        "reading": "국어 - 읽기",
        "writing": "국어 - 쓰기",
        "grammar": "국어 - 문법",
        "literature": "국어 - 문학",
        "mediaLiteracy": "국어 - 매체",
        "numbersOperations": "수학 - 수와 연산",
        "changeAndRelations": "수학 - 변화와 관계",
        "geometryMeasurement": "수학 - 도형과 측정",
        "dataAndProbability": "수학 - 자료와 가능성",
    }
    
    # 선택된 도메인만 출력
    for domain_key, domain_name in domain_names.items():
        if domain_key in weekly_materials_data:
            materials_list = weekly_materials_data[domain_key]
            
            # 도메인별 소제목
            doc.add_heading(domain_name, level=3)
            
            # 주차별 자료 출력
            if isinstance(materials_list, list):
                for item in materials_list:
                    if isinstance(item, dict):
                        week = item.get('week', '?')
                        material_url = item.get('material_url', '링크 없음')
                        doc.add_paragraph(
                            f"[{week}주차] {material_url}",
                            style='List Bullet 2'
                        )
            
            doc.add_paragraph()  # 간격
    
    if not any(key in weekly_materials_data for key in domain_names.keys()):
        doc.add_paragraph("⚠️ 학습 자료 데이터가 없습니다.", style='Intense Quote')


__all__ = [
    "generate_docx_for_iep",
    "generate_docx_stream",
    "DocumentGenerationError",
    "DocumentNotFoundError",
    "InvalidDocumentDataError",
]


