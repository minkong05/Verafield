import uuid

from sqlalchemy.orm import Session

from backend.db.models.mill import Mill
from packages.shared_types.mill import MillCreate

__all__ = [
    "MillAlreadyExistsError",
    "MillNotFoundError",
    "create_mill",
    "get_mill",
    "update_mill",
    "list_mills",
]


class MillNotFoundError(Exception):
    """No mill is registered with the given id."""


class MillAlreadyExistsError(Exception):
    """A mill is already registered with that MPOB licence number."""


def get_mill(db: Session, mill_id: uuid.UUID) -> Mill:
    mill = db.query(Mill).filter(Mill.id == mill_id).one_or_none()
    if mill is None:
        raise MillNotFoundError(f"no mill registered with id {mill_id}")
    return mill


def list_mills(db: Session) -> list[Mill]:
    """Every registered mill. The one cross-tenant read in this codebase —
    it enumerates the entire customer base, so its route is admin-only."""
    return db.query(Mill).order_by(Mill.name).all()


def create_mill(db: Session, payload: MillCreate) -> Mill:
    """Register a mill at onboarding.

    The duplicate-licence check is a SELECT-then-INSERT rather than catching
    IntegrityError, matching every other *AlreadyExistsError in this codebase.
    Accepted race: two concurrent registrations of the same licence produce
    one 409 and one 500 from uq_mills_mpob_licence_number. Noted rather than
    hidden because this is the first endpoint whose unique key is
    client-supplied and human-meaningful, so the collision is plausible rather
    than theoretical — the constraint still holds either way, which is the
    part that matters."""
    existing = (
        db.query(Mill).filter(Mill.mpob_licence_number == payload.mpob_licence_number).one_or_none()
    )
    if existing is not None:
        raise MillAlreadyExistsError(
            f"a mill is already registered with MPOB licence number {payload.mpob_licence_number}"
        )

    mill = Mill(
        name=payload.name,
        mpob_licence_number=payload.mpob_licence_number,
        postal_address=payload.postal_address,
        email=payload.email,
        district=payload.district,
        state=payload.state,
    )
    db.add(mill)
    db.commit()
    db.refresh(mill)
    return mill


def update_mill(db: Session, mill: Mill, changes: dict[str, object]) -> Mill:
    """Apply an already-authorised partial update.

    *Which* fields a caller may change depends on their role, so that check
    belongs in the route; this enforces only the invariant that outlives any
    caller — mpob_licence_number stays unique, so an edit can no more mint a
    duplicate tenant identity than a registration can."""
    licence = changes.get("mpob_licence_number")
    if licence is not None and licence != mill.mpob_licence_number:
        clash = (
            db.query(Mill)
            .filter(Mill.mpob_licence_number == licence, Mill.id != mill.id)
            .one_or_none()
        )
        if clash is not None:
            raise MillAlreadyExistsError(
                f"a mill is already registered with MPOB licence number {licence}"
            )

    for field, value in changes.items():
        setattr(mill, field, value)
    db.commit()
    db.refresh(mill)
    return mill
