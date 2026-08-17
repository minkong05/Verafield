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
from shared_types.enums import DeforestationStatus

if TYPE_CHECKING:
    from backend.db.models.plot import Plot

_deforestation_status_type = SAEnum(
    DeforestationStatus, name="deforestation_status", values_callable=lambda e: [m.value for m in e]
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
