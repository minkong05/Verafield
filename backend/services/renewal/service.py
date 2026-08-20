import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.db.models.evidence_pack import BatchPlot, EvidencePack
from backend.db.models.household import Household
from backend.db.models.plot import Plot
from backend.services.gap_assessment.service import get_household

__all__ = [
    "HouseholdRenewalStatus",
    "add_one_year",
    "compute_renewal_due_at",
    "get_household_renewal_status",
    "get_latest_evidence_pack_generated_at",
    "household_renewal_is_lapsed",
    "list_mill_renewal_status",
]


def add_one_year(value: datetime) -> datetime:
    """Same calendar date one year later, preserving time-of-day/tz. Falls
    back to 1 March if value is 29 Feb and the target year isn't a leap
    year — two consecutive years are never both leap years, so any
    29-Feb-anchored due date hits this exactly once."""
    try:
        return value.replace(year=value.year + 1)
    except ValueError:
        return value.replace(year=value.year + 1, month=3, day=1)


def get_latest_evidence_pack_generated_at(
    db: Session, mill_id: uuid.UUID, household_id: uuid.UUID
) -> datetime | None:
    """Max EvidencePack.generated_at across every batch touching any of this
    household's plots. Mirrors dashboard.service._household_has_evidence_pack's
    Plot -> BatchPlot -> batch_ids -> EvidencePack traversal, generalized to a
    value via func.max() instead of a boolean .first() check. None if the
    household has no plots, no batches, or no evidence pack yet."""
    plot_ids = [
        row.id
        for row in db.query(Plot.id)
        .filter(Plot.household_id == household_id, Plot.mill_id == mill_id)
        .all()
    ]
    if not plot_ids:
        return None

    batch_ids = {
        row.batch_id
        for row in db.query(BatchPlot.batch_id)
        .filter(BatchPlot.plot_id.in_(plot_ids), BatchPlot.mill_id == mill_id)
        .all()
    }
    if not batch_ids:
        return None

    return (
        db.query(func.max(EvidencePack.generated_at))
        .filter(EvidencePack.batch_id.in_(batch_ids), EvidencePack.mill_id == mill_id)
        .scalar()
    )


def compute_renewal_due_at(
    db: Session, mill_id: uuid.UUID, household_id: uuid.UUID
) -> datetime | None:
    """None if the household has no evidence pack yet — nothing to renew."""
    generated_at = get_latest_evidence_pack_generated_at(db, mill_id, household_id)
    return add_one_year(generated_at) if generated_at is not None else None


def _is_lapsed(due_at: datetime | None, as_of: datetime) -> bool:
    return due_at is not None and as_of >= due_at


def household_renewal_is_lapsed(
    db: Session, mill_id: uuid.UUID, household_id: uuid.UUID, *, as_of: datetime | None = None
) -> bool:
    """Cheap boolean, no household-existence check — same precedent as
    dashboard.service._household_has_evidence_pack. This is what
    dashboard.service.compute_household_status calls. as_of defaults to
    real now(); the keyword exists so tests can pin the comparison instant
    instead of racing wall-clock time at an exact boundary."""
    due_at = compute_renewal_due_at(db, mill_id, household_id)
    return _is_lapsed(due_at, as_of if as_of is not None else datetime.now(UTC))


@dataclass(frozen=True)
class HouseholdRenewalStatus:
    household: Household
    last_evidence_pack_generated_at: datetime | None
    renewal_due_at: datetime | None
    lapsed: bool


def get_household_renewal_status(
    db: Session, mill_id: uuid.UUID, household_id: uuid.UUID, *, as_of: datetime | None = None
) -> HouseholdRenewalStatus:
    """Raises HouseholdNotFoundError (via get_household) if household_id
    doesn't belong to mill_id — the route-facing 404 path."""
    household = get_household(db, mill_id, household_id)
    generated_at = get_latest_evidence_pack_generated_at(db, mill_id, household.id)
    due_at = add_one_year(generated_at) if generated_at is not None else None
    lapsed = _is_lapsed(due_at, as_of if as_of is not None else datetime.now(UTC))
    return HouseholdRenewalStatus(
        household=household,
        last_evidence_pack_generated_at=generated_at,
        renewal_due_at=due_at,
        lapsed=lapsed,
    )


def list_mill_renewal_status(
    db: Session, mill_id: uuid.UUID, *, as_of: datetime | None = None
) -> list[HouseholdRenewalStatus]:
    households = (
        db.query(Household)
        .filter(Household.mill_id == mill_id)
        .order_by(Household.created_at)
        .all()
    )
    return [
        get_household_renewal_status(db, mill_id, household.id, as_of=as_of)
        for household in households
    ]
