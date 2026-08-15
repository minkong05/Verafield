import uuid

from sqlalchemy.orm import Session

from backend.db.models.gap_assessment import GapAssessment, GapAssessmentItem
from backend.db.models.household import Household
from shared_types.enums import EvidenceCategory
from shared_types.gap_assessment import GapAssessmentCreate, GapAssessmentItemCreate
from shared_types.household import HouseholdCreate


class HouseholdNotFoundError(Exception):
    """No household exists for the given (mill_id, household_id) pair."""


class GapAssessmentNotFoundError(Exception):
    """The household exists but has no gap assessment yet."""


class GapAssessmentAlreadyExistsError(Exception):
    """A household may have at most one gap assessment for MVP."""


class InvalidChecklistError(Exception):
    """Submitted items don't cover exactly the six fixed categories once each."""


def validate_checklist_items(items: list[GapAssessmentItemCreate]) -> None:
    categories = [item.category for item in items]
    if len(categories) != len(set(categories)):
        raise InvalidChecklistError("duplicate evidence category in submitted items")
    if set(categories) != set(EvidenceCategory):
        missing = set(EvidenceCategory) - set(categories)
        raise InvalidChecklistError(
            f"missing required evidence categories: {sorted(c.value for c in missing)}"
        )


def create_household(db: Session, mill_id: uuid.UUID, payload: HouseholdCreate) -> Household:
    household = Household(mill_id=mill_id, name=payload.name)
    db.add(household)
    db.commit()
    db.refresh(household)
    return household


def get_household(db: Session, mill_id: uuid.UUID, household_id: uuid.UUID) -> Household:
    household = (
        db.query(Household)
        .filter(Household.id == household_id, Household.mill_id == mill_id)
        .one_or_none()
    )
    if household is None:
        raise HouseholdNotFoundError(f"household {household_id} not found for mill {mill_id}")
    return household


def create_gap_assessment(
    db: Session, mill_id: uuid.UUID, household_id: uuid.UUID, payload: GapAssessmentCreate
) -> GapAssessment:
    household = get_household(db, mill_id, household_id)
    validate_checklist_items(payload.items)

    existing = (
        db.query(GapAssessment)
        .filter(GapAssessment.household_id == household.id, GapAssessment.mill_id == mill_id)
        .one_or_none()
    )
    if existing is not None:
        raise GapAssessmentAlreadyExistsError(
            f"gap assessment already exists for household {household_id}"
        )

    assessment = GapAssessment(
        mill_id=mill_id, household_id=household.id, assessed_by=payload.assessed_by
    )
    assessment.items = [
        GapAssessmentItem(
            mill_id=mill_id, category=item.category, status=item.status, notes=item.notes
        )
        for item in payload.items
    ]
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment


def get_gap_assessment(db: Session, mill_id: uuid.UUID, household_id: uuid.UUID) -> GapAssessment:
    get_household(db, mill_id, household_id)  # 404s if this household isn't this mill's
    assessment = (
        db.query(GapAssessment)
        .filter(GapAssessment.household_id == household_id, GapAssessment.mill_id == mill_id)
        .one_or_none()
    )
    if assessment is None:
        raise GapAssessmentNotFoundError(f"no gap assessment yet for household {household_id}")
    return assessment
