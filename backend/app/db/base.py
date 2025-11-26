from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """모든 ORM 모델의 베이스"""
    pass


# Import all models here for metadata.create_all()
from app.models.student import Student  # noqa: E402, F401
from app.models.iep_version import IEPVersion  # noqa: E402, F401
