from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from .iep_version import IEPVersion


class IEPFile(Base):
    """IEP 파일 모델 - 메타데이터만 저장 (실제 파일은 디스크)"""
    
    __tablename__ = "iep_file"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    iep_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("iep_version.id", ondelete="CASCADE"),
        nullable=False,
    )
    file_type: Mapped[str] = mapped_column(nullable=False)  # "goals", "weekly_plan", "weekly_materials"
    file_path: Mapped[str] = mapped_column(nullable=False)  # 디스크 경로
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationship
    iep_version: Mapped["IEPVersion"] = relationship(back_populates="iep_files")
