import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from shared_types.enums import DocumentType, LandOwnershipStatus, LandType, MalaysiaState


class LandDocumentRuleRequirement(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    document_type: DocumentType
    is_hard_fail: bool


class LandDocumentRule(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    rule_version: str
    state: MalaysiaState
    land_type: LandType
    requirements: list[LandDocumentRuleRequirement]


class LandOwnershipAssessmentCreate(BaseModel):
    state: MalaysiaState
    land_type: LandType
    assessed_by: str
    documents_collected: list[DocumentType]


class LandOwnershipAssessment(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    mill_id: uuid.UUID
    household_id: uuid.UUID
    state: MalaysiaState
    land_type: LandType
    rule_version: str
    status: LandOwnershipStatus
    assessed_by: str
    assessed_at: datetime
    documents_collected: list[DocumentType]
