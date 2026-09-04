import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.routes.dependencies import get_current_user, require_admin, validate_mill
from backend.services.gap_assessment.service import HouseholdNotFoundError
from backend.services.rules_engine import service
from packages.shared_types import LandDocumentRule as LandDocumentRuleSchema
from packages.shared_types import LandOwnershipAssessment as LandOwnershipAssessmentSchema
from packages.shared_types import LandOwnershipAssessmentCreate
from packages.shared_types.enums import LandType, MalaysiaState

router = APIRouter(tags=["rules-engine"])


@router.get(
    "/land-ownership-rules/{state}/{land_type}",
    response_model=LandDocumentRuleSchema,
    # The Land Document Playbook is core in-house IP and global reference
    # data: any authenticated principal may read it, and it stays
    # mill-free — no tenant scoping, no 403 between mills.
    dependencies=[Depends(get_current_user)],
)
def read_land_document_rule(
    state: MalaysiaState, land_type: LandType, db: Session = Depends(get_db)
) -> LandDocumentRuleSchema:
    try:
        rule = service.get_rule(db, state, land_type)
    except service.RuleNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return LandDocumentRuleSchema.model_validate(rule)


@router.post(
    "/mills/{mill_id}/households/{household_id}/land-ownership-assessment",
    response_model=LandOwnershipAssessmentSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin), Depends(validate_mill)],
)
def create_land_ownership_assessment(
    mill_id: uuid.UUID,
    household_id: uuid.UUID,
    payload: LandOwnershipAssessmentCreate,
    db: Session = Depends(get_db),
) -> LandOwnershipAssessmentSchema:
    try:
        assessment = service.create_land_ownership_assessment(db, mill_id, household_id, payload)
    except HouseholdNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except service.RuleNotFoundError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)) from exc
    except service.LandOwnershipAssessmentAlreadyExistsError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return LandOwnershipAssessmentSchema.model_validate(assessment)


@router.get(
    "/mills/{mill_id}/households/{household_id}/land-ownership-assessment",
    response_model=LandOwnershipAssessmentSchema,
    dependencies=[Depends(require_admin), Depends(validate_mill)],
)
def read_land_ownership_assessment(
    mill_id: uuid.UUID, household_id: uuid.UUID, db: Session = Depends(get_db)
) -> LandOwnershipAssessmentSchema:
    try:
        assessment = service.get_land_ownership_assessment(db, mill_id, household_id)
    except (HouseholdNotFoundError, service.LandOwnershipAssessmentNotFoundError) as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return LandOwnershipAssessmentSchema.model_validate(assessment)
