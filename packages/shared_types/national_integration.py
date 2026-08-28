import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from shared_types.enums import FieldVerificationStatus


class NationalSystemsLookupCreate(BaseModel):
    mpob_licence_number: str
    sims_transaction_volume_kg: Decimal = Field(gt=0, decimal_places=2)
    regional_yield_benchmark_kg_per_ha: Decimal = Field(gt=0, decimal_places=2)
    geosawit_mapping_exists: bool
    geosawit_reference: str | None = None
    emspo_certification_status: str
    looked_up_by: str


class NationalSystemsLookup(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    mill_id: uuid.UUID
    household_id: uuid.UUID
    mpob_licence_number: str
    sims_transaction_volume_kg: Decimal
    declared_area_ha: Decimal
    regional_yield_benchmark_kg_per_ha: Decimal
    volume_yield_mismatch: bool
    geosawit_mapping_exists: bool
    geosawit_reference: str | None
    emspo_certification_status: str
    status: FieldVerificationStatus
    looked_up_by: str
    looked_up_at: datetime
