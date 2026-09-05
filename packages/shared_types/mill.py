import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from shared_types.enums import MalaysiaState


class MillBase(BaseModel):
    name: str
    mpob_licence_number: str
    postal_address: str
    email: str
    district: str
    state: MalaysiaState


class MillCreate(MillBase):
    pass


class Mill(MillBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID

    is_active: bool
    created_at: datetime
    updated_at: datetime


class MillUpdate(BaseModel):
    """Every field optional. Which of them a given caller may set is a
    question of role, not of shape, so it is enforced in the route against
    model_fields_set rather than by a second narrower schema: a mill user
    editing its own contact details sends the same body an admin would."""

    name: str | None = None
    mpob_licence_number: str | None = None
    postal_address: str | None = None
    email: str | None = None
    district: str | None = None
    state: MalaysiaState | None = None
    is_active: bool | None = None
