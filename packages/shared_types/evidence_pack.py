import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from shared_types.enums import (
    DeforestationStatus,
    DocumentType,
    LandOwnershipStatus,
    LandType,
    MalaysiaState,
    NoMixingStatus,
)


class BatchPlotCreate(BaseModel):
    plot_id: uuid.UUID
    harvest_date: date


class BatchCreate(BaseModel):
    product_description: str
    trade_name: str
    hs_code: str
    net_mass_kg: Decimal = Field(gt=0, decimal_places=2)
    recipient_name: str
    recipient_postal_address: str
    recipient_email: str
    created_by: str
    plots: list[BatchPlotCreate] = Field(min_length=1)

    @model_validator(mode="after")
    def _plot_ids_are_unique(self) -> "BatchCreate":
        plot_ids = [item.plot_id for item in self.plots]
        if len(plot_ids) != len(set(plot_ids)):
            raise ValueError("duplicate plot_id in batch composition")
        return self


class BatchPlot(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    mill_id: uuid.UUID
    batch_id: uuid.UUID
    plot_id: uuid.UUID
    harvest_date: date


class Batch(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    mill_id: uuid.UUID
    product_description: str
    trade_name: str
    hs_code: str
    net_mass_kg: Decimal
    recipient_name: str
    recipient_postal_address: str
    recipient_email: str
    no_mixing_status: NoMixingStatus
    created_by: str
    created_at: datetime
    plots: list[BatchPlot]


class EvidencePackCreate(BaseModel):
    generated_by: str


class EvidencePackSupplier(BaseModel):
    household_id: uuid.UUID
    name: str
    postal_address: str
    email: str
    district: str
    state: MalaysiaState


class EvidencePackPlotGeolocation(BaseModel):
    plot_id: uuid.UUID
    household_id: uuid.UUID
    centroid_lat: Decimal
    centroid_lon: Decimal
    area_ha: Decimal
    harvest_date: date


class EvidencePackDeforestationEvidence(BaseModel):
    plot_id: uuid.UUID
    status: DeforestationStatus
    reviewed_by: str
    reviewed_at: datetime


class EvidencePackLegalityEvidence(BaseModel):
    household_id: uuid.UUID
    land_type: LandType
    rule_version: str
    status: LandOwnershipStatus
    documents_collected: list[DocumentType]


class EvidencePackAssembly(BaseModel):
    """The Annex II / Article 9(1) field mapping (tech.md Table 42). Stored
    verbatim (via model_dump(mode="json")) as EvidencePack.assembled_data — a
    snapshot at generation time, never recomputed on read."""

    product_description: str
    trade_name: str
    hs_code: str
    net_mass_kg: Decimal
    country_of_production: str
    plots: list[EvidencePackPlotGeolocation]
    production_date_start: date
    production_date_end: date
    suppliers: list[EvidencePackSupplier]
    recipient_name: str
    recipient_postal_address: str
    recipient_email: str
    deforestation_evidence: list[EvidencePackDeforestationEvidence]
    legality_evidence: list[EvidencePackLegalityEvidence]
    no_mixing_status: NoMixingStatus


class EvidencePack(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    mill_id: uuid.UUID
    batch_id: uuid.UUID
    assembled_data: EvidencePackAssembly
    geojson: dict
    generated_by: str
    generated_at: datetime
