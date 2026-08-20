import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.services.gap_assessment.service import HouseholdNotFoundError
from backend.services.national_integration import service
from shared_types import NationalSystemsLookup as NationalSystemsLookupSchema
from shared_types import NationalSystemsLookupCreate

router = APIRouter(
    prefix="/mills/{mill_id}/households/{household_id}", tags=["national-integration"]
)


@router.post(
    "/national-systems-lookup",
    response_model=NationalSystemsLookupSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_national_systems_lookup(
    mill_id: uuid.UUID,
    household_id: uuid.UUID,
    payload: NationalSystemsLookupCreate,
    db: Session = Depends(get_db),
) -> NationalSystemsLookupSchema:
    try:
        lookup = service.create_national_systems_lookup(db, mill_id, household_id, payload)
    except HouseholdNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except service.NationalSystemsLookupAlreadyExistsError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return NationalSystemsLookupSchema.model_validate(lookup)


@router.get("/national-systems-lookup", response_model=NationalSystemsLookupSchema)
def read_national_systems_lookup(
    mill_id: uuid.UUID, household_id: uuid.UUID, db: Session = Depends(get_db)
) -> NationalSystemsLookupSchema:
    try:
        lookup = service.get_national_systems_lookup(db, mill_id, household_id)
    except (HouseholdNotFoundError, service.NationalSystemsLookupNotFoundError) as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return NationalSystemsLookupSchema.model_validate(lookup)
