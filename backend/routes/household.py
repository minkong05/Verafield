import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.routes.dependencies import authorize_mill
from backend.services.gap_assessment import service
from packages.shared_types import Household as HouseholdSchema
from packages.shared_types import HouseholdCreate

router = APIRouter(
    prefix="/mills/{mill_id}/households",
    tags=["households"],
    dependencies=[Depends(authorize_mill)],
)


@router.post("", response_model=HouseholdSchema, status_code=status.HTTP_201_CREATED)
def create_household(
    mill_id: uuid.UUID,
    payload: HouseholdCreate,
    db: Session = Depends(get_db),
) -> HouseholdSchema:
    household = service.create_household(db, mill_id, payload)
    return HouseholdSchema.model_validate(household)
