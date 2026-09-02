import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.services.dashboard import service
from packages.shared_types import MillDashboardSupplier

router = APIRouter(prefix="/mills/{mill_id}/dashboard", tags=["dashboard"])


@router.get("", response_model=list[MillDashboardSupplier])
def read_dashboard(
    mill_id: uuid.UUID, db: Session = Depends(get_db)
) -> list[MillDashboardSupplier]:
    return [
        MillDashboardSupplier(
            household_id=household.id,
            mill_id=household.mill_id,
            name=household.name,
            district=household.district,
            status=status,
        )
        for household, status in service.list_mill_dashboard(db, mill_id)
    ]
