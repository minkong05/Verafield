import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, model_validator

from shared_types.enums import DeforestationStatus

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
