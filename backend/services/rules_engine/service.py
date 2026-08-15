import uuid

from sqlalchemy.orm import Session

from backend.db.models.rules_engine import (
    LandDocumentRule,
    LandOwnershipAssessment,
    LandOwnershipDocument,
)
from backend.services.gap_assessment.service import get_household
from shared_types.enums import DocumentType, LandOwnershipStatus, LandType, MalaysiaState
from shared_types.rules_engine import LandOwnershipAssessmentCreate

CURRENT_RULE_VERSION = "sabah-sarawak-v1"


class RuleNotFoundError(Exception):
    """No rule exists for the given (rule_version, state, land_type)."""


class LandOwnershipAssessmentNotFoundError(Exception):
    """The household exists but has no land ownership assessment yet."""


class LandOwnershipAssessmentAlreadyExistsError(Exception):
    """A household may have at most one land ownership assessment for MVP."""


def compute_status(
    required: set[DocumentType], hard_fail: set[DocumentType], collected: set[DocumentType]
) -> LandOwnershipStatus:
    missing = required - collected
    if not missing:
        return LandOwnershipStatus.CLEARED
    if missing & hard_fail:
        return LandOwnershipStatus.FAILED
    return LandOwnershipStatus.NEEDS_FOLLOW_UP


def get_rule(db: Session, state: MalaysiaState, land_type: LandType) -> LandDocumentRule:
    rule = (
        db.query(LandDocumentRule)
        .filter(
            LandDocumentRule.rule_version == CURRENT_RULE_VERSION,
            LandDocumentRule.state == state,
            LandDocumentRule.land_type == land_type,
        )
        .one_or_none()
    )
    if rule is None:
        raise RuleNotFoundError(f"no rule for state {state} and land type {land_type}")
    return rule


def create_land_ownership_assessment(
    db: Session, mill_id: uuid.UUID, household_id: uuid.UUID, payload: LandOwnershipAssessmentCreate
) -> LandOwnershipAssessment:
    household = get_household(db, mill_id, household_id)
    rule = get_rule(db, payload.state, payload.land_type)

    existing = (
        db.query(LandOwnershipAssessment)
        .filter(
            LandOwnershipAssessment.household_id == household.id,
            LandOwnershipAssessment.mill_id == mill_id,
        )
        .one_or_none()
    )
    if existing is not None:
        raise LandOwnershipAssessmentAlreadyExistsError(
            f"land ownership assessment already exists for household {household_id}"
        )

    required = {req.document_type for req in rule.requirements}
    hard_fail = {req.document_type for req in rule.requirements if req.is_hard_fail}
    collected = set(payload.documents_collected)
    status = compute_status(required, hard_fail, collected)

    assessment = LandOwnershipAssessment(
        mill_id=mill_id,
        household_id=household.id,
        state=payload.state,
        land_type=payload.land_type,
        rule_id=rule.id,
        status=status,
        assessed_by=payload.assessed_by,
    )
    assessment.documents = [
        LandOwnershipDocument(mill_id=mill_id, document_type=document_type)
        for document_type in collected
    ]
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment


def get_land_ownership_assessment(
    db: Session, mill_id: uuid.UUID, household_id: uuid.UUID
) -> LandOwnershipAssessment:
    get_household(db, mill_id, household_id)  # 404s if this household isn't this mill's
    assessment = (
        db.query(LandOwnershipAssessment)
        .filter(
            LandOwnershipAssessment.household_id == household_id,
            LandOwnershipAssessment.mill_id == mill_id,
        )
        .one_or_none()
    )
    if assessment is None:
        raise LandOwnershipAssessmentNotFoundError(
            f"no land ownership assessment yet for household {household_id}"
        )
    return assessment
