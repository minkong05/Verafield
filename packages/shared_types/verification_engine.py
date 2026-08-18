import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from shared_types.enums import DeforestationStatus, FieldVerificationStatus

_BASELINE_CUTOFF = date(2020, 12, 31)


class DeforestationCheckCreate(BaseModel):
    forest_area_ha: Decimal
    tree_height_m: Decimal
    canopy_cover_pct: Decimal
    predominantly_agricultural_or_urban: bool
    pre_2020_imagery_date: date
    post_2020_imagery_date: date
    forest_loss_detected: bool
    review_inconclusive: bool = False
    reviewed_by: str

    @model_validator(mode="after")
    def _imagery_dates_straddle_the_cutoff(self) -> "DeforestationCheckCreate":
        if self.pre_2020_imagery_date > _BASELINE_CUTOFF:
            raise ValueError("pre_2020_imagery_date must be on or before 2020-12-31")
        if self.post_2020_imagery_date <= _BASELINE_CUTOFF:
            raise ValueError("post_2020_imagery_date must be after 2020-12-31")
        return self


class DeforestationCheck(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    mill_id: uuid.UUID
    plot_id: uuid.UUID
    forest_area_ha: Decimal
    tree_height_m: Decimal
    canopy_cover_pct: Decimal
    predominantly_agricultural_or_urban: bool
    pre_2020_imagery_date: date
    post_2020_imagery_date: date
    forest_loss_detected: bool
    review_inconclusive: bool
    reviewed_by: str
    reviewed_at: datetime
    status: DeforestationStatus


class FieldVerificationCheckCreate(BaseModel):
    gnss_checkin_lat: Decimal = Field(ge=-90, le=90, decimal_places=6)
    gnss_checkin_lon: Decimal = Field(ge=-180, le=180, decimal_places=6)
    gnss_checkin_at: datetime
    photo_lat: Decimal = Field(ge=-90, le=90, decimal_places=6)
    photo_lon: Decimal = Field(ge=-180, le=180, decimal_places=6)
    photo_taken_at: datetime
    title_area_ha: Decimal = Field(gt=0, decimal_places=4)
    recorded_by: str


class FieldVerificationCheck(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    mill_id: uuid.UUID
    plot_id: uuid.UUID
    gnss_checkin_lat: Decimal
    gnss_checkin_lon: Decimal
    gnss_checkin_at: datetime
    photo_lat: Decimal
    photo_lon: Decimal
    photo_taken_at: datetime
    title_area_ha: Decimal
    checkin_mismatch: bool
    photo_mismatch: bool
    area_mismatch: bool
    status: FieldVerificationStatus
    recorded_by: str
    recorded_at: datetime


class YieldLicenceCheckCreate(BaseModel):
    mpob_licensed_area_ha: Decimal = Field(gt=0, decimal_places=4)
    annual_output_kg: Decimal = Field(gt=0, decimal_places=2)
    regional_yield_benchmark_kg_per_ha: Decimal = Field(gt=0, decimal_places=2)
    recorded_by: str


class YieldLicenceCheck(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    mill_id: uuid.UUID
    household_id: uuid.UUID
    mpob_licensed_area_ha: Decimal
    declared_area_ha: Decimal
    annual_output_kg: Decimal
    regional_yield_benchmark_kg_per_ha: Decimal
    licence_mismatch: bool
    yield_mismatch: bool
    status: FieldVerificationStatus
    recorded_by: str
    recorded_at: datetime
