import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from shared_types.enums import SignatureMethod


class LabourDeclarationCreate(BaseModel):
    labour_arrangement_description: str
    no_child_labour_confirmed: bool
    has_land_dispute: bool
    land_dispute_notes: str | None = None
    signature_method: SignatureMethod
    collected_by: str
    collected_at: datetime


class LabourDeclaration(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    mill_id: uuid.UUID
    household_id: uuid.UUID
    labour_arrangement_description: str
    no_child_labour_confirmed: bool
    has_land_dispute: bool
    land_dispute_notes: str | None
    signature_method: SignatureMethod
    collected_by: str
    collected_at: datetime


class ConsentRecordCreate(BaseModel):
    mykad_last4: str = Field(pattern=r"^\d{4}$")
    credit_referral_consent_given: bool = False
    signature_method: SignatureMethod
    collected_by: str
    collected_at: datetime


class ConsentRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    mill_id: uuid.UUID
    household_id: uuid.UUID
    mykad_last4: str
    credit_referral_consent_given: bool
    signature_method: SignatureMethod
    collected_by: str
    collected_at: datetime
