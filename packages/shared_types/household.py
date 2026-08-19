import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class HouseholdBase(BaseModel):
    name: str
    postal_address: str
    email: str
    district: str


class HouseholdCreate(HouseholdBase):
    pass


class Household(HouseholdBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    mill_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
