"""
Student API 테스트

학생 생성 및 조회 API 테스트
"""
import pytest
from datetime import date


@pytest.mark.unit
def test_create_student(client):
    """
    POST /students - 학생 생성 테스트
    
    검증:
    - 201 Created 응답
    - 반환된 JSON에 id, name, birth 포함
    """
    student_data = {
        "name": "김철수",
        "birth": "2015-05-20"
    }
    
    response = client.post("/students", json=student_data)
    
    assert response.status_code == 201
    data = response.json()
    
    assert "id" in data
    assert data["name"] == "김철수"
    assert data["birth"] == "2015-05-20"


@pytest.mark.unit
def test_list_students(client, sample_student):
    """
    GET /students - 학생 목록 조회 테스트
    
    검증:
    - 200 OK 응답
    - 생성된 학생이 목록에 포함됨
    """
    response = client.get("/students")
    
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    assert len(data) >= 1
    
    # sample_student가 목록에 있는지 확인
    student_ids = [str(s["id"]) for s in data]
    assert str(sample_student.id) in student_ids


@pytest.mark.unit
def test_create_multiple_students(client):
    """
    여러 학생 생성 및 조회 테스트
    
    검증:
    - 여러 학생 생성 가능
    - 목록 조회 시 모두 포함
    """
    students = [
        {"name": "학생1", "birth": "2015-01-01"},
        {"name": "학생2", "birth": "2015-02-02"},
        {"name": "학생3", "birth": "2015-03-03"},
    ]
    
    created_ids = []
    for student_data in students:
        response = client.post("/students", json=student_data)
        assert response.status_code == 201
        created_ids.append(response.json()["id"])
    
    # 목록 조회
    response = client.get("/students")
    assert response.status_code == 200
    data = response.json()
    
    assert len(data) >= 3
    retrieved_ids = [s["id"] for s in data]
    for created_id in created_ids:
        assert created_id in retrieved_ids
