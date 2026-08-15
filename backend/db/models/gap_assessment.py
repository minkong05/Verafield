import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKeyConstraint, Index, String, Text, UniqueConstraint, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base
from shared_types.enums import EvidenceCategory, GapStatus

if TYPE_CHECKING:
    from backend.db.models.household import Household

# str Enum members would otherwise store their NAME in the native Postgres
# enum type; values_callable forces the lower_snake_case .value instead, so
# the DB column and the JSON wire value are identical strings.
_evidence_category_type = SAEnum(
    EvidenceCategory, name="evidence_category", values_callable=lambda e: [m.value for m in e]
)
_gap_status_type = SAEnum(
    GapStatus, name="gap_status", values_callable=lambda e: [m.value for m in e]
)


class GapAssessment(Base):
    __tablename__ = "gap_assessments"
    __table_args__ = (
        ForeignKeyConstraint(
            ["household_id", "mill_id"],
            ["households.id", "households.mill_id"],
            name="fk_gap_assessments_household_mill",
            ondelete="CASCADE",
        ),
        UniqueConstraint("id", "mill_id", name="uq_gap_assessments_id_mill_id"),
        # One assessment per household for MVP — no versioning/re-assessment yet.
        UniqueConstraint("household_id", name="uq_gap_assessments_household_id"),
        Index("ix_gap_assessments_mill_id", "mill_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    mill_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    household_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    assessed_by: Mapped[str] = mapped_column(String(255), nullable=False)
    assessed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    household: Mapped["Household"] = relationship(back_populates="gap_assessment")
    items: Mapped[list["GapAssessmentItem"]] = relationship(
        back_populates="gap_assessment",
        cascade="all, delete-orphan",
        order_by="GapAssessmentItem.category",
    )


class GapAssessmentItem(Base):
    __tablename__ = "gap_assessment_items"
    __table_args__ = (
        ForeignKeyConstraint(
            ["gap_assessment_id", "mill_id"],
            ["gap_assessments.id", "gap_assessments.mill_id"],
            name="fk_gap_assessment_items_assessment_mill",
            ondelete="CASCADE",
        ),
        UniqueConstraint(
            "gap_assessment_id", "category", name="uq_gap_assessment_items_assessment_category"
        ),
        Index("ix_gap_assessment_items_mill_id", "mill_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    mill_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    gap_assessment_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    category: Mapped[EvidenceCategory] = mapped_column(_evidence_category_type, nullable=False)
    status: Mapped[GapStatus] = mapped_column(_gap_status_type, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    gap_assessment: Mapped["GapAssessment"] = relationship(back_populates="items")
