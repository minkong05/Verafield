import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    ForeignKeyConstraint,
    Index,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base

if TYPE_CHECKING:
    from backend.db.models.household import Household


class Plot(Base):
    """A household's land parcel: geolocation only, one household may have
    many plots (unlike every other MVP entity, deliberately no
    UniqueConstraint("household_id", ...) here). collected_at/collected_by
    are client-supplied, not server-stamped, matching LabourDeclaration:
    capture happens on-site/offline via the field app and Feature 05
    cross-checks this timestamp against GPS/photo signals. Polygon is stored
    as plain JSONB ([lon, lat] pairs, float) rather than a PostGIS geometry
    column — no spatial queries are needed for MVP, only storage/round-trip
    toward Feature 06's GeoJSON output, so no new dependency was added."""

    __tablename__ = "plots"
    __table_args__ = (
        ForeignKeyConstraint(
            ["household_id", "mill_id"],
            ["households.id", "households.mill_id"],
            name="fk_plots_household_mill",
            ondelete="CASCADE",
        ),
        UniqueConstraint("id", "mill_id", name="uq_plots_id_mill_id"),
        Index("ix_plots_mill_id", "mill_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    mill_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    household_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    polygon: Mapped[list] = mapped_column(JSONB, nullable=False)
    # Numeric, not Float: compared against literal legal thresholds elsewhere
    # in the system (Feature 04's forest three-threshold test), so binary
    # float rounding is not an acceptable risk here.
    centroid_lat: Mapped[Decimal] = mapped_column(Numeric(8, 6), nullable=False)
    centroid_lon: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
    area_ha: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    collected_by: Mapped[str] = mapped_column(String(255), nullable=False)
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    household: Mapped["Household"] = relationship(back_populates="plots")
