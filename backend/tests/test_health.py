"""
헬스체크 엔드포인트 테스트

앱이 정상적으로 시작되고 헬스체크 API가 동작하는지 확인
"""
import pytest


@pytest.mark.unit
def test_health_check(client):
    """
    GET /health 엔드포인트 테스트
    
    검증:
    - 200 OK 응답
    - 정상 상태 메시지 포함
    """
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "status" in data
    assert data["status"] == "healthy"

