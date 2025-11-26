"""IEPVersion 모델 및 API 테스트"""
from __future__ import annotations


def test_import_iep_version_model():
    """IEPVersion 모델 임포트 테스트"""
    from app.models.iep_version import IEPVersion
    assert IEPVersion.__tablename__ == "iep_version"


def test_import_iep_version_schemas():
    """IEPVersion 스키마 임포트 테스트"""
    from app.schemas.iep_version import IEPVersionCreate, IEPVersionResponse
    assert IEPVersionCreate is not None
    assert IEPVersionResponse is not None


def test_import_iep_version_router():
    """IEPVersion 라우터 임포트 테스트"""
    from app.api.iep_versions import router
    assert router is not None
    assert "IEP Versions" in router.tags

