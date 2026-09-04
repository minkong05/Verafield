import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, UniqueConstraint, func, true
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.base import Base
from packages.shared_types.enums import MalaysiaState

_malaysia_state_type = SAEnum(
    MalaysiaState, name="malaysia_state", values_callable=lambda e: [m.value for m in e]
)


class Mill(Base):
    """The tenant root: one row per onboarded mill, so the mill_id every other
    table carries resolves to a named, licensed operator instead of an
    arbitrary UUID a caller invented.

    Deliberately has no mill_id column and no UNIQUE(id, mill_id), unlike
    every other tenant table: mills.id *is* the mill_id, so children reference
    it with a plain single-column FK that is already the whole tenant key.
    backend/db/README.md's composite-FK pattern exists to bind a child to a
    parent *within* a tenant, and there is no tenant above a mill. This is the
    third documented exception to that hard rule, alongside LandDocumentRule
    (no mill_id at all — global reference data) and Plot (no per-household
    unique). Do not "fix" it by adding one.

    Children reference this table with RESTRICT, not the CASCADE used
    everywhere else: every existing CASCADE is child->parent within a tenant,
    whereas DELETE FROM mills under CASCADE would silently destroy a tenant's
    entire five-year evidence trail (Articles 9(1), 4(3), 12(5)). No DELETE
    route exists anywhere in this codebase, so RESTRICT costs nothing.

    mpob_licence_number is the *mill's own* licence, unrelated to
    NationalSystemsLookup.mpob_licence_number (Feature 08), which is the
    *smallholder household's* — different subject, different table, no
    collision, and no reason to add a unique constraint to that one. Its
    UNIQUE constraint here is the anti-duplicate-tenant guard: re-registering
    the same mill returns 409 rather than minting a second tenant.

    is_active revokes a mill's access without deleting it (Feature 11's
    "revocable without deleting the mill"). It is not a soft-delete — rows are
    never removed, and an admin still reaches an inactive mill's data."""

    __tablename__ = "mills"
    __table_args__ = (UniqueConstraint("mpob_licence_number", name="uq_mills_mpob_licence_number"),)

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    mpob_licence_number: Mapped[str] = mapped_column(String(64), nullable=False)
    postal_address: Mapped[str] = mapped_column(String(500), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    district: Mapped[str] = mapped_column(String(255), nullable=False)
    state: Mapped[MalaysiaState] = mapped_column(_malaysia_state_type, nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=true()
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
