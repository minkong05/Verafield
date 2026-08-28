import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Date,
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
from shared_types.enums import DeforestationStatus, FieldVerificationStatus

if TYPE_CHECKING:
    from backend.db.models.household import Household
    from backend.db.models.plot import Plot

_deforestation_status_type = SAEnum(
    DeforestationStatus, name="deforestation_status", values_callable=lambda e: [m.value for m in e]
)
_field_verification_status_type = SAEnum(
    FieldVerificationStatus,
    name="field_verification_status",
    values_callable=lambda e: [m.value for m in e],
)


class DeforestationCheck(Base):
    """One per plot for MVP (mirrors GapAssessment/LandOwnershipAssessment/
    LabourDeclaration's "one per X" pattern, keyed on plot_id instead of
    household_id). reviewed_at is server-stamped, unlike Plot's client-supplied
    collected_at: the GIS specialist's review happens off-site against
    imagery, with no on-site signal to cross-check it against, so this
    mirrors LandOwnershipAssessment.assessed_at instead of
    LabourDeclaration.collected_at. status is computed once at create time by
    verification_engine.service.compute_status from the fields below."""

    __tablename__ = "deforestation_checks"
    __table_args__ = (
        ForeignKeyConstraint(
            ["plot_id", "mill_id"],
            ["plots.id", "plots.mill_id"],
            name="fk_deforestation_checks_plot_mill",
            ondelete="CASCADE",
        ),
        UniqueConstraint("id", "mill_id", name="uq_deforestation_checks_id_mill_id"),
        UniqueConstraint("plot_id", name="uq_deforestation_checks_plot_id"),
        Index("ix_deforestation_checks_mill_id", "mill_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    mill_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    plot_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    forest_area_ha: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    tree_height_m: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    canopy_cover_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    predominantly_agricultural_or_urban: Mapped[bool] = mapped_column(Boolean, nullable=False)
    pre_2020_imagery_date: Mapped[date] = mapped_column(Date, nullable=False)
    post_2020_imagery_date: Mapped[date] = mapped_column(Date, nullable=False)
    forest_loss_detected: Mapped[bool] = mapped_column(Boolean, nullable=False)
    review_inconclusive: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    reviewed_by: Mapped[str] = mapped_column(String(255), nullable=False)
    reviewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    status: Mapped[DeforestationStatus] = mapped_column(_deforestation_status_type, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    plot: Mapped["Plot"] = relationship()


class FieldVerificationCheck(Base):
    """One per plot for MVP (mirrors DeforestationCheck's plot_id-keyed
    pattern). gnss_checkin_at/photo_taken_at are client-supplied, unlike
    recorded_at: these are the on-site capture instants Feature 05 exists to
    cross-check, so they must reflect what the device actually recorded, not
    when this record was synced/reviewed. Compares against the plot's own
    centroid_lat/centroid_lon/collected_at/area_ha rather than duplicating
    them here. status is computed once at create time by
    verification_engine.service.compute_field_verification_status."""

    __tablename__ = "field_verification_checks"
    __table_args__ = (
        ForeignKeyConstraint(
            ["plot_id", "mill_id"],
            ["plots.id", "plots.mill_id"],
            name="fk_field_verification_checks_plot_mill",
            ondelete="CASCADE",
        ),
        UniqueConstraint("id", "mill_id", name="uq_field_verification_checks_id_mill_id"),
        UniqueConstraint("plot_id", name="uq_field_verification_checks_plot_id"),
        Index("ix_field_verification_checks_mill_id", "mill_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    mill_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    plot_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    gnss_checkin_lat: Mapped[Decimal] = mapped_column(Numeric(8, 6), nullable=False)
    gnss_checkin_lon: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
    gnss_checkin_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    photo_lat: Mapped[Decimal] = mapped_column(Numeric(8, 6), nullable=False)
    photo_lon: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
    photo_taken_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    title_area_ha: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    checkin_mismatch: Mapped[bool] = mapped_column(Boolean, nullable=False)
    photo_mismatch: Mapped[bool] = mapped_column(Boolean, nullable=False)
    area_mismatch: Mapped[bool] = mapped_column(Boolean, nullable=False)
    status: Mapped[FieldVerificationStatus] = mapped_column(
        _field_verification_status_type, nullable=False
    )
    recorded_by: Mapped[str] = mapped_column(String(255), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    plot: Mapped["Plot"] = relationship()


class YieldLicenceCheck(Base):
    """One per household for MVP (mirrors LandOwnershipAssessment's
    household_id-keyed pattern). declared_area_ha is a snapshot computed by
    verification_engine.service.create_yield_licence_check as the sum of the
    household's Plot.area_ha at check time, stored rather than recomputed
    live, so an audit later reproduces the exact figures the check ran
    against even if plots changed afterward — same rationale as
    LandOwnershipAssessment storing rule_id. status is computed once at
    create time by verification_engine.service.compute_yield_licence_status."""

    __tablename__ = "yield_licence_checks"
    __table_args__ = (
        ForeignKeyConstraint(
            ["household_id", "mill_id"],
            ["households.id", "households.mill_id"],
            name="fk_yield_licence_checks_household_mill",
            ondelete="CASCADE",
        ),
        UniqueConstraint("id", "mill_id", name="uq_yield_licence_checks_id_mill_id"),
        UniqueConstraint("household_id", name="uq_yield_licence_checks_household_id"),
        Index("ix_yield_licence_checks_mill_id", "mill_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    mill_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    household_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    mpob_licensed_area_ha: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    declared_area_ha: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    annual_output_kg: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    regional_yield_benchmark_kg_per_ha: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False
    )
    licence_mismatch: Mapped[bool] = mapped_column(Boolean, nullable=False)
    yield_mismatch: Mapped[bool] = mapped_column(Boolean, nullable=False)
    status: Mapped[FieldVerificationStatus] = mapped_column(
        _field_verification_status_type, nullable=False
    )
    recorded_by: Mapped[str] = mapped_column(String(255), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    household: Mapped["Household"] = relationship()
