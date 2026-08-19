import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Index, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base

if TYPE_CHECKING:
    from backend.db.models.gap_assessment import GapAssessment
    from backend.db.models.plot import Plot


class Household(Base):
    """Smallholder profile. Tenant-scoped: one mill per household — a
    smallholder supplying two mills gets two separate Household rows
    (tech.md §6.4)."""

    __tablename__ = "households"
    __table_args__ = (
        UniqueConstraint("id", "mill_id", name="uq_households_id_mill_id"),
        Index("ix_households_mill_id", "mill_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    mill_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    postal_address: Mapped[str] = mapped_column(String(500), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    district: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    gap_assessment: Mapped["GapAssessment | None"] = relationship(
        back_populates="household", uselist=False
    )
    plots: Mapped[list["Plot"]] = relationship(back_populates="household")
