import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.services.gap_assessment import service
from packages.shared_types import GapAssessment as GapAssessmentSchema
from packages.shared_types import GapAssessmentCreate

router = APIRouter(prefix="/mills/{mill_id}/households/{household_id}", tags=["gap-assessment"])


@router.post(
    "/gap-assessment", response_model=GapAssessmentSchema, status_code=status.HTTP_201_CREATED
)
def create_gap_assessment(
    mill_id: uuid.UUID,
    household_id: uuid.UUID,
    payload: GapAssessmentCreate,
    db: Session = Depends(get_db),
) -> GapAssessmentSchema:
    try:
        assessment = service.create_gap_assessment(db, mill_id, household_id, payload)
    except service.HouseholdNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except service.InvalidChecklistError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)) from exc
    except service.GapAssessmentAlreadyExistsError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return GapAssessmentSchema.model_validate(assessment)


@router.get("/gap-assessment", response_model=GapAssessmentSchema)
def read_gap_assessment(
    mill_id: uuid.UUID, household_id: uuid.UUID, db: Session = Depends(get_db)
) -> GapAssessmentSchema:
    try:
        assessment = service.get_gap_assessment(db, mill_id, household_id)
    except (service.HouseholdNotFoundError, service.GapAssessmentNotFoundError) as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return GapAssessmentSchema.model_validate(assessment)
