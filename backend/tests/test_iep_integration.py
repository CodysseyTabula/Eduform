"""
IEP 파일 생성 통합 테스트 (AI 모듈 모킹 포함)

IEP 파일 생성 API가 AI 모듈을 호출하고 3개의 파일을 생성하는지 검증
"""
import json
import pytest
from pathlib import Path


@pytest.mark.integration
def test_create_iep_files_with_ai_mock(
    client,
    sample_iep_version,
    sample_student_profile,
    mock_ai_generators,
    tmp_storage_path,
    db_session
):
    """
    POST /iep-files - IEP 파일 생성 통합 테스트 (AI 모듈 모킹)
    
    검증:
    - AI 모듈 호출 (모킹됨)
    - 3개의 JSON 파일이 디스크에 생성됨
    - 3개의 IEPFile 레코드가 DB에 저장됨
    """
    # student_profile을 JSON 파일로 변환
    profile_json = json.dumps(sample_student_profile, ensure_ascii=False).encode('utf-8')
    
    # multipart/form-data 요청
    files = {
        "file": ("student_profile.json", profile_json, "application/json")
    }
    data = {
        "iep_version_id": str(sample_iep_version.id)
    }
    
    response = client.post("/iep-files", files=files, data=data)
    
    # API 응답 확인
    assert response.status_code == 201
    data = response.json()
    
    assert isinstance(data, list)
    assert len(data) == 3
    
    # 반환된 파일 타입 확인
    file_types = {item["file_type"] for item in data}
    assert file_types == {"goals", "weekly_plan", "weekly_materials"}
    
    # 디스크 파일 확인
    iep_version_dir = tmp_storage_path / "iep" / str(sample_iep_version.id)
    assert iep_version_dir.exists()
    
    # 3개 파일이 존재하는지 확인
    json_files = list(iep_version_dir.glob("*.json"))
    assert len(json_files) == 3
    
    # 각 파일 내용 확인
    for item in data:
        file_path = Path(item["file_path"])
        assert file_path.exists()
        
        # JSON 파싱 가능한지 확인
        with open(file_path, "r", encoding="utf-8") as f:
            content = json.load(f)
            assert isinstance(content, dict)
            
        # 파일 타입별 내용 검증
        if item["file_type"] == "goals":
            assert "reading" in content or "numbersOperations" in content
        elif item["file_type"] == "weekly_plan":
            assert "reading" in content or "numbersOperations" in content
        elif item["file_type"] == "weekly_materials":
            assert "reading" in content or "numbersOperations" in content


@pytest.mark.integration
def test_iep_files_query(client, sample_iep_version, mock_ai_generators, sample_student_profile):
    """
    GET /iep-versions/{iep_version_id}/iep-files - IEP 파일 조회 테스트
    
    검증:
    - IEP 파일 생성 후 조회 가능
    - 3개 파일 메타데이터 반환
    """
    # 먼저 IEP 파일 생성 (multipart/form-data)
    profile_json = json.dumps(sample_student_profile, ensure_ascii=False).encode('utf-8')
    files = {
        "file": ("student_profile.json", profile_json, "application/json")
    }
    data = {
        "iep_version_id": str(sample_iep_version.id)
    }
    
    create_response = client.post("/iep-files", files=files, data=data)
    assert create_response.status_code == 201
    
    # 파일 조회
    response = client.get(f"/iep-versions/{sample_iep_version.id}/iep-files")
    
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    assert len(data) == 3
    
    # 각 파일에 필수 필드 확인
    for item in data:
        assert "id" in item
        assert "file_type" in item
        assert "file_path" in item
        assert item["file_type"] in ["goals", "weekly_plan", "weekly_materials"]


@pytest.mark.integration
def test_mock_ai_data_structure(mock_ai_generators):
    """
    AI 모듈 모킹 데이터 구조 검증
    
    mock_ai_generators fixture가 올바른 구조를 반환하는지 확인
    """
    mock_data = mock_ai_generators
    
    # 3개 키 존재 확인
    assert "goals" in mock_data
    assert "weekly_plan" in mock_data
    assert "weekly_materials" in mock_data
    
    # goals 구조 확인
    goals = mock_data["goals"]
    assert isinstance(goals, dict)
    assert "reading" in goals
    assert "annual_goal" in goals["reading"]
    assert "semester_goal" in goals["reading"]
    
    # weekly_plan 구조 확인
    weekly_plan = mock_data["weekly_plan"]
    assert isinstance(weekly_plan, dict)
    assert "reading" in weekly_plan
    assert isinstance(weekly_plan["reading"], list)
    assert len(weekly_plan["reading"]) == 20
    
    # weekly_materials 구조 확인
    weekly_materials = mock_data["weekly_materials"]
    assert isinstance(weekly_materials, dict)
    assert "reading" in weekly_materials
    assert isinstance(weekly_materials["reading"], list)
    assert len(weekly_materials["reading"]) == 20

