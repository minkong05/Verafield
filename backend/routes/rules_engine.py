import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.services.gap_assessment.service import HouseholdNotFoundError
from backend.services.rules_engine import service
from shared_types import LandDocumentRule as LandDocumentRuleSchema
from shared_types import LandOwnershipAssessment as LandOwnershipAssessmentSchema
from shared_types import LandOwnershipAssessmentCreate
from shared_types.enums import LandType, MalaysiaState

router = APIRouter(tags=["rules-engine"])


@router.get("/land-ownership-rules/{state}/{land_type}", response_model=LandDocumentRuleSchema)
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
)
def read_land_ownership_assessment(
    mill_id: uuid.UUID, household_id: uuid.UUID, db: Session = Depends(get_db)
) -> LandOwnershipAssessmentSchema:
    try:
        assessment = service.get_land_ownership_assessment(db, mill_id, household_id)
    except (HouseholdNotFoundError, service.LandOwnershipAssessmentNotFoundError) as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return LandOwnershipAssessmentSchema.model_validate(assessment)
