import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKeyConstraint,
    Index,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base
from packages.shared_types.enums import FieldVerificationStatus

if TYPE_CHECKING:
    from backend.db.models.household import Household

_field_verification_status_type = SAEnum(
    FieldVerificationStatus,
    name="field_verification_status",
    values_callable=lambda e: [m.value for m in e],
)


class NationalSystemsLookup(Base):
    """One per household for MVP (mirrors YieldLicenceCheck's
    household_id-keyed pattern) — a compliance analyst's manually-entered
    snapshot of what SIMS/GeoSAWIT/e-MSPO show for this household's MPOB
    licence number, standing in for a live read-only feed into those systems
    (tech.md schedules that integration for Sprint 4, post-pilot). Reuses the
    field_verification_status enum rather than introducing a new one.
    declared_area_ha is a snapshot computed by
    national_integration.service.create_national_systems_lookup as the sum of
    the household's Plot.area_ha at lookup time, stored rather than
    recomputed live — same rationale as YieldLicenceCheck.declared_area_ha.
    looked_up_at is server-stamped, unlike Plot.collected_at: this is an
    off-system lookup with no on-site signal to cross-check it against, so it
    mirrors DeforestationCheck.reviewed_at instead."""

    __tablename__ = "national_systems_lookups"
    __table_args__ = (
        ForeignKeyConstraint(
            ["household_id", "mill_id"],
            ["households.id", "households.mill_id"],
            name="fk_national_systems_lookups_household_mill",
            ondelete="CASCADE",
        ),
        UniqueConstraint("id", "mill_id", name="uq_national_systems_lookups_id_mill_id"),
        UniqueConstraint("household_id", name="uq_national_systems_lookups_household_id"),
        Index("ix_national_systems_lookups_mill_id", "mill_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    mill_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    household_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    mpob_licence_number: Mapped[str] = mapped_column(String(64), nullable=False)
    sims_transaction_volume_kg: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    declared_area_ha: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    regional_yield_benchmark_kg_per_ha: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False
    )
    volume_yield_mismatch: Mapped[bool] = mapped_column(Boolean, nullable=False)
    geosawit_mapping_exists: Mapped[bool] = mapped_column(Boolean, nullable=False)
    geosawit_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    emspo_certification_status: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[FieldVerificationStatus] = mapped_column(
        _field_verification_status_type, nullable=False
    )
    looked_up_by: Mapped[str] = mapped_column(String(255), nullable=False)
    looked_up_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    household: Mapped["Household"] = relationship()
