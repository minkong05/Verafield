import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from shared_types.enums import EvidenceCategory, GapStatus


class GapAssessmentItemBase(BaseModel):
    category: EvidenceCategory
    status: GapStatus
    notes: str | None = None


class GapAssessmentItemCreate(GapAssessmentItemBase):
    pass


class GapAssessmentItem(GapAssessmentItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID


class GapAssessmentCreate(BaseModel):
    assessed_by: str
    items: list[GapAssessmentItemCreate]


class GapAssessment(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    mill_id: uuid.UUID
    household_id: uuid.UUID
    assessed_by: str
    assessed_at: datetime
    items: list[GapAssessmentItem]
