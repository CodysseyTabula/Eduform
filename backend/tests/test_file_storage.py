"""
파일 저장 서비스 테스트
"""

import os
import uuid
from pathlib import Path

import pytest

from app.services.file_storage import (
    FileStorageError,
    load_json_file,
    save_json_file,
)


def test_import():
    """모듈 import 테스트"""
    from app.services.file_storage import save_json_file, load_json_file
    assert save_json_file is not None
    assert load_json_file is not None


def test_save_and_load_json_file(tmp_path, monkeypatch):
    """JSON 파일 저장 및 로드 기능 테스트"""
    # 임시 storage path 설정
    from app.core.config import settings
    monkeypatch.setattr(settings, "storage_path", str(tmp_path))
    
    # 테스트 데이터
    test_id = str(uuid.uuid4())
    test_content = {
        "test": "data",
        "한글": "테스트",
        "nested": {"key": "value"}
    }
    
    # 저장
    file_path = save_json_file(test_id, "goal", test_content)
    
    # 검증: 파일 존재
    assert os.path.exists(file_path)
    assert file_path.endswith(".json")
    assert "goal-" in file_path
    assert str(test_id) in file_path
    
    # 로드
    loaded_content = load_json_file(file_path)
    
    # 검증: 내용 일치
    assert loaded_content == test_content
    assert loaded_content["test"] == "data"
    assert loaded_content["한글"] == "테스트"


def test_save_creates_directory(tmp_path, monkeypatch):
    """디렉토리 자동 생성 테스트"""
    from app.core.config import settings
    monkeypatch.setattr(settings, "storage_path", str(tmp_path))
    
    test_id = str(uuid.uuid4())
    file_path = save_json_file(test_id, "weekly_plan", {"week": 1})
    
    expected_dir = tmp_path / "iep" / test_id
    assert expected_dir.exists()
    assert expected_dir.is_dir()


def test_load_nonexistent_file():
    """존재하지 않는 파일 로드 시 예외 발생 테스트"""
    with pytest.raises(FileStorageError, match="File not found"):
        load_json_file("/nonexistent/path/file.json")


def test_load_invalid_json(tmp_path):
    """잘못된 JSON 파일 로드 시 예외 발생 테스트"""
    invalid_file = tmp_path / "invalid.json"
    invalid_file.write_text("{ invalid json }", encoding="utf-8")
    
    with pytest.raises(FileStorageError, match="Invalid JSON"):
        load_json_file(str(invalid_file))


def test_load_non_dict_json(tmp_path):
    """JSON 배열(non-dict) 로드 시 예외 발생 테스트"""
    array_file = tmp_path / "array.json"
    array_file.write_text("[1, 2, 3]", encoding="utf-8")
    
    with pytest.raises(FileStorageError, match="Expected JSON object"):
        load_json_file(str(array_file))


def test_multiple_files_same_version(tmp_path, monkeypatch):
    """같은 버전에 여러 파일 저장 테스트"""
    from app.core.config import settings
    monkeypatch.setattr(settings, "storage_path", str(tmp_path))
    
    test_id = str(uuid.uuid4())
    
    # 여러 파일 타입 저장
    path1 = save_json_file(test_id, "goal", {"type": "goal"})
    path2 = save_json_file(test_id, "weekly_plan", {"type": "plan"})
    path3 = save_json_file(test_id, "material", {"type": "material"})
    
    # 모두 같은 디렉토리에 있어야 함
    assert Path(path1).parent == Path(path2).parent == Path(path3).parent
    
    # 각각 로드 가능
    assert load_json_file(path1)["type"] == "goal"
    assert load_json_file(path2)["type"] == "plan"
    assert load_json_file(path3)["type"] == "material"

