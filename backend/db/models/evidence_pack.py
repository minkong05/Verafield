import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
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
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base
from shared_types.enums import NoMixingStatus

if TYPE_CHECKING:
    from backend.db.models.plot import Plot

_no_mixing_status_type = SAEnum(
    NoMixingStatus, name="no_mixing_status", values_callable=lambda e: [m.value for m in e]
)


class Batch(Base):
    """A mill's shipment batch: manual-entry product/recipient fields, since
    no Mill table exists (mill_id is a bare UUID everywhere in this codebase
    — see backend/db/README.md). Immutable after creation, like every other
    MVP entity (no PATCH routes exist anywhere in this codebase).
    no_mixing_status is computed once at create time by
    evidence_pack.service.compute_no_mixing_status from this batch's
    BatchPlot rows' distinct plot count."""

    __tablename__ = "batches"
    __table_args__ = (
        UniqueConstraint("id", "mill_id", name="uq_batches_id_mill_id"),
        Index("ix_batches_mill_id", "mill_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    mill_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    product_description: Mapped[str] = mapped_column(String(255), nullable=False)
    trade_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hs_code: Mapped[str] = mapped_column(String(20), nullable=False)
    net_mass_kg: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    recipient_name: Mapped[str] = mapped_column(String(255), nullable=False)
    recipient_postal_address: Mapped[str] = mapped_column(String(500), nullable=False)
    recipient_email: Mapped[str] = mapped_column(String(255), nullable=False)
    no_mixing_status: Mapped[NoMixingStatus] = mapped_column(_no_mixing_status_type, nullable=False)
    created_by: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    plots: Mapped[list["BatchPlot"]] = relationship(
        back_populates="batch", cascade="all, delete-orphan", order_by="BatchPlot.harvest_date"
    )
    evidence_pack: Mapped["EvidencePack | None"] = relationship(
        back_populates="batch", uselist=False
    )


class BatchPlot(Base):
    """This plot's contribution to this batch, plus the harvest date for that
    contribution. Plot itself has no harvest_date column — a plot is
    harvested repeatedly over time, so a static column there would only ever
    hold the most recent harvest. The first join table in this codebase with
    two independent composite-FK parents (batch, plot).
    UniqueConstraint("batch_id", "plot_id") stops a plot appearing twice in
    one batch, but deliberately not UniqueConstraint("plot_id") alone: a
    plot legitimately contributes to many batches over time (mirrors Plot's
    own "no UniqueConstraint(household_id, ...)" precedent)."""

    __tablename__ = "batch_plots"
    __table_args__ = (
        ForeignKeyConstraint(
            ["batch_id", "mill_id"],
            ["batches.id", "batches.mill_id"],
            name="fk_batch_plots_batch_mill",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["plot_id", "mill_id"],
            ["plots.id", "plots.mill_id"],
            name="fk_batch_plots_plot_mill",
            ondelete="CASCADE",
        ),
        UniqueConstraint("id", "mill_id", name="uq_batch_plots_id_mill_id"),
        UniqueConstraint("batch_id", "plot_id", name="uq_batch_plots_batch_id_plot_id"),
        Index("ix_batch_plots_mill_id", "mill_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    mill_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    batch_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    plot_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    harvest_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    batch: Mapped["Batch"] = relationship(back_populates="plots")
    # overlaps: mill_id is always set explicitly at construction (never
    # populated via cascade from either parent), so the two relationships
    # "competing" to write batch_plots.mill_id is a false positive — silence
    # per SQLAlchemy's own guidance rather than leave the warning live.
    plot: Mapped["Plot"] = relationship(overlaps="batch,plots")


class EvidencePack(Base):
    """One per batch for MVP (mirrors GapAssessment's "one per X" pattern,
    keyed on batch_id). assembled_data/geojson are snapshots computed once by
    evidence_pack.service.generate_evidence_pack and stored, never
    recomputed on read — same rationale as YieldLicenceCheck.declared_area_ha:
    an audit years later must see exactly what the pack contained when
    generated, even if the underlying plots/checks changed afterward."""

    __tablename__ = "evidence_packs"
    __table_args__ = (
        ForeignKeyConstraint(
            ["batch_id", "mill_id"],
            ["batches.id", "batches.mill_id"],
            name="fk_evidence_packs_batch_mill",
            ondelete="CASCADE",
        ),
        UniqueConstraint("id", "mill_id", name="uq_evidence_packs_id_mill_id"),
        UniqueConstraint("batch_id", name="uq_evidence_packs_batch_id"),
        Index("ix_evidence_packs_mill_id", "mill_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    mill_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    batch_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    assembled_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    geojson: Mapped[dict] = mapped_column(JSONB, nullable=False)
    generated_by: Mapped[str] = mapped_column(String(255), nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    batch: Mapped["Batch"] = relationship(back_populates="evidence_pack")
