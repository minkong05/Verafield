import uuid

from sqlalchemy.orm import Session

from backend.db.models.evidence_pack import BatchPlot, EvidencePack
from backend.db.models.household import Household
from backend.db.models.plot import Plot
from backend.db.models.verification_engine import FieldVerificationCheck, YieldLicenceCheck
from backend.services.renewal.service import household_renewal_is_lapsed
from packages.shared_types.enums import FieldVerificationStatus, MillDashboardStatus

__all__ = ["compute_household_status", "list_mill_dashboard"]


def _household_has_unresolved_signal(
    db: Session, mill_id: uuid.UUID, household_id: uuid.UUID
) -> bool:
    plots = db.query(Plot).filter(Plot.household_id == household_id, Plot.mill_id == mill_id).all()
    for plot in plots:
        field_check = (
            db.query(FieldVerificationCheck)
            .filter(
                FieldVerificationCheck.plot_id == plot.id,
                FieldVerificationCheck.mill_id == mill_id,
            )
            .one_or_none()
        )
        if field_check is not None and field_check.status == FieldVerificationStatus.NEEDS_REVIEW:
            return True

    yield_check = (
        db.query(YieldLicenceCheck)
        .filter(
            YieldLicenceCheck.household_id == household_id, YieldLicenceCheck.mill_id == mill_id
        )
        .one_or_none()
    )
    return yield_check is not None and yield_check.status == FieldVerificationStatus.NEEDS_REVIEW


def _household_has_evidence_pack(db: Session, mill_id: uuid.UUID, household_id: uuid.UUID) -> bool:
    plot_ids = [
        row.id
        for row in db.query(Plot.id)
        .filter(Plot.household_id == household_id, Plot.mill_id == mill_id)
        .all()
    ]
    if not plot_ids:
        return False

    batch_ids = {
        row.batch_id
        for row in db.query(BatchPlot.batch_id)
        .filter(BatchPlot.plot_id.in_(plot_ids), BatchPlot.mill_id == mill_id)
        .all()
    }
    if not batch_ids:
        return False

    return (
        db.query(EvidencePack)
        .filter(EvidencePack.batch_id.in_(batch_ids), EvidencePack.mill_id == mill_id)
        .first()
        is not None
    )


def compute_household_status(
    db: Session, mill_id: uuid.UUID, household_id: uuid.UUID
) -> MillDashboardStatus:
    """frozen takes priority over cleared: a household whose evidence pack
    predates a newly-raised Feature 05 flag, or whose renewal has lapsed
    (Feature 09), must still show frozen, not a stale cleared. Deliberately
    does not call verification_engine.service.household_is_cleared, which
    answers a different, forward-looking question (see dashboard/README.md)."""
    if _household_has_unresolved_signal(db, mill_id, household_id):
        return MillDashboardStatus.FROZEN
    has_evidence_pack = _household_has_evidence_pack(db, mill_id, household_id)
    if has_evidence_pack and household_renewal_is_lapsed(db, mill_id, household_id):
        return MillDashboardStatus.FROZEN
    if has_evidence_pack:
        return MillDashboardStatus.CLEARED
    return MillDashboardStatus.PENDING


def list_mill_dashboard(
    db: Session, mill_id: uuid.UUID
) -> list[tuple[Household, MillDashboardStatus]]:
    households = (
        db.query(Household)
        .filter(Household.mill_id == mill_id)
        .order_by(Household.created_at)
        .all()
    )
    return [
        (household, compute_household_status(db, mill_id, household.id)) for household in households
    ]
