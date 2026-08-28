import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKeyConstraint,
    Index,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base
from packages.shared_types.enums import SignatureMethod

if TYPE_CHECKING:
    from backend.db.models.household import Household

_signature_method_type = SAEnum(
    SignatureMethod, name="signature_method", values_callable=lambda e: [m.value for m in e]
)


class LabourDeclaration(Base):
    """One per household for MVP (mirrors GapAssessment/LandOwnershipAssessment).
    collected_at/collected_by are client-supplied, not server-stamped: capture
    happens on-site and offline, syncing later, and Feature 05 cross-checks
    this timestamp against other on-site signals (GPS check-in, photo geotag)."""

    __tablename__ = "labour_declarations"
    __table_args__ = (
        ForeignKeyConstraint(
            ["household_id", "mill_id"],
            ["households.id", "households.mill_id"],
            name="fk_labour_declarations_household_mill",
            ondelete="CASCADE",
        ),
        UniqueConstraint("id", "mill_id", name="uq_labour_declarations_id_mill_id"),
        UniqueConstraint("household_id", name="uq_labour_declarations_household_id"),
        Index("ix_labour_declarations_mill_id", "mill_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    mill_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    household_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    labour_arrangement_description: Mapped[str] = mapped_column(Text, nullable=False)
    no_child_labour_confirmed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_land_dispute: Mapped[bool] = mapped_column(Boolean, nullable=False)
    land_dispute_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    signature_method: Mapped[SignatureMethod] = mapped_column(
        _signature_method_type, nullable=False
    )
    collected_by: Mapped[str] = mapped_column(String(255), nullable=False)
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    household: Mapped["Household"] = relationship()


class ConsentRecord(Base):
    """One per household for MVP. Dual-track PDPA/GDPR consent (tech.md §6.4):
    mykad_last4 is identity-minimised (never a full MyKad scan), and
    credit_referral_consent_given is a separate, explicit opt-in line on the
    same instrument — its truth is dated by collected_at, no separate
    timestamp (one signing event)."""

    __tablename__ = "consent_records"
    __table_args__ = (
        ForeignKeyConstraint(
            ["household_id", "mill_id"],
            ["households.id", "households.mill_id"],
            name="fk_consent_records_household_mill",
            ondelete="CASCADE",
        ),
        UniqueConstraint("id", "mill_id", name="uq_consent_records_id_mill_id"),
        UniqueConstraint("household_id", name="uq_consent_records_household_id"),
        Index("ix_consent_records_mill_id", "mill_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    mill_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    household_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    mykad_last4: Mapped[str] = mapped_column(String(4), nullable=False)
    credit_referral_consent_given: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    signature_method: Mapped[SignatureMethod] = mapped_column(
        _signature_method_type, nullable=False
    )
    collected_by: Mapped[str] = mapped_column(String(255), nullable=False)
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    household: Mapped["Household"] = relationship()
