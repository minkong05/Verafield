import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.services.gap_assessment.service import HouseholdNotFoundError
from backend.services.renewal import service
from shared_types import RenewalStatus as RenewalStatusSchema

router = APIRouter(prefix="/mills/{mill_id}", tags=["renewal"])


def _to_schema(entry: service.HouseholdRenewalStatus) -> RenewalStatusSchema:
    return RenewalStatusSchema(
        household_id=entry.household.id,
        mill_id=entry.household.mill_id,
        name=entry.household.name,
        district=entry.household.district,
        last_evidence_pack_generated_at=entry.last_evidence_pack_generated_at,
        renewal_due_at=entry.renewal_due_at,
        lapsed=entry.lapsed,
    )


@router.get("/households/{household_id}/renewal-status", response_model=RenewalStatusSchema)
def read_household_renewal_status(
    mill_id: uuid.UUID, household_id: uuid.UUID, db: Session = Depends(get_db)
) -> RenewalStatusSchema:
    try:
        entry = service.get_household_renewal_status(db, mill_id, household_id)
    except HouseholdNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return _to_schema(entry)


@router.get("/renewal-status", response_model=list[RenewalStatusSchema])
def read_mill_renewal_status(
    mill_id: uuid.UUID, db: Session = Depends(get_db)
) -> list[RenewalStatusSchema]:
    return [_to_schema(entry) for entry in service.list_mill_renewal_status(db, mill_id)]
