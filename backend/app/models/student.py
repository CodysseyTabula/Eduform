from __future__ import annotations

import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from .iep_version import IEPVersion


class Student(Base):
    """학생 기본 정보 모델"""
    
    __tablename__ = "student"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str]
    birth: Mapped[date]

    # Relationships (IEPVersion 모델 구현 전까지 임시 주석 처리)
    # iep_versions: Mapped[list["IEPVersion"]] = relationship(
    #     back_populates="student",
    #     cascade="all, delete-orphan",
    # )
