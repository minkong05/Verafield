import uuid
from datetime import datetime

from pydantic import BaseModel


class RenewalStatus(BaseModel):
    household_id: uuid.UUID
    mill_id: uuid.UUID
    name: str
    district: str
    last_evidence_pack_generated_at: datetime | None
    renewal_due_at: datetime | None
    lapsed: bool
