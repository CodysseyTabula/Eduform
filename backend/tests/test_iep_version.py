"""
IEPVersion API 테스트

IEP 버전 생성 및 조회 API 테스트
"""
import pytest


@pytest.mark.unit
def test_create_iep_version(client, sample_student):
    """
    POST /iep-versions - IEP 버전 생성 테스트
    
    검증:
    - 201 Created 응답
    - 반환된 JSON에 id, year, semester, grade 포함
    """
    version_data = {
        "student_id": str(sample_student.id),
        "year": "2024",
        "semester": "1학기",
        "grade": "3"
    }
    
    response = client.post("/iep-versions", json=version_data)
    
    assert response.status_code == 201
    data = response.json()
    
    assert "id" in data
    assert data["year"] == "2024"
    assert data["semester"] == "1학기"
    assert data["grade"] == "3"


@pytest.mark.unit
def test_get_student_iep_versions(client, sample_iep_version):
    """
    GET /students/{student_id}/iep-versions - 학생 IEP 버전 목록 조회
    
    검증:
    - 200 OK 응답
    - 생성된 IEP 버전이 목록에 포함됨
    """
    student_id = sample_iep_version.student_id
    
    response = client.get(f"/students/{student_id}/iep-versions")
    
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    assert len(data) >= 1
    
    # sample_iep_version이 목록에 있는지 확인
    version_ids = [v["id"] for v in data]
    assert str(sample_iep_version.id) in version_ids


@pytest.mark.unit
def test_get_latest_iep_version(client, sample_iep_version):
    """
    GET /students/{student_id}/iep-latest - 학생 최신 IEP 조회
    
    검증:
    - 200 OK 응답
    - 최신 IEP 버전 반환
    """
    student_id = sample_iep_version.student_id
    
    response = client.get(f"/students/{student_id}/iep-latest")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["id"] == str(sample_iep_version.id)
    assert data["year"] == "2024"
    assert data["semester"] == "1학기"

