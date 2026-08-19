import uuid

from pydantic import BaseModel

from shared_types.enums import MillDashboardStatus


class MillDashboardSupplier(BaseModel):
    household_id: uuid.UUID
    mill_id: uuid.UUID
    name: str
    district: str
    status: MillDashboardStatus
