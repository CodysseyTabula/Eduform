"""
모든 ORM 모델을 한 곳에서 import하여 Base.metadata가 인식하도록 함
"""

from app.models.student import Student  # noqa
from app.models.iep_version import IEPVersion  # noqa

__all__ = ["Student", "IEPVersion"]

