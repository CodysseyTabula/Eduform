from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from .student import Student
    from .iep_file import IEPFile


class IEPVersion(Base):
    """IEP 버전 모델 - 학기별 IEP 관리"""
    
    __tablename__ = "iep_version"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("student.id", ondelete="CASCADE"),
        nullable=False,
    )
    year: Mapped[str] = mapped_column(nullable=False)
    semester: Mapped[str] = mapped_column(nullable=False)
    grade: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    student: Mapped["Student"] = relationship(back_populates="iep_versions")
    iep_files: Mapped[list["IEPFile"]] = relationship(
        back_populates="iep_version",
        cascade="all, delete-orphan",
    )

