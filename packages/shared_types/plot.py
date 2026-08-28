import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PlotCreate(BaseModel):
    polygon: list[list[float]] = Field(min_length=3)
    centroid_lat: Decimal = Field(ge=-90, le=90, decimal_places=6)
    centroid_lon: Decimal = Field(ge=-180, le=180, decimal_places=6)
    area_ha: Decimal = Field(gt=0, decimal_places=4)
    collected_by: str
    collected_at: datetime

    @field_validator("polygon")
    @classmethod
    def _points_are_lon_lat_pairs(cls, value: list[list[float]]) -> list[list[float]]:
        if any(len(point) != 2 for point in value):
            raise ValueError("each polygon point must be a [lon, lat] pair")
        return value


class Plot(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    mill_id: uuid.UUID
    household_id: uuid.UUID
    polygon: list[list[float]]
    centroid_lat: Decimal
    centroid_lon: Decimal
    area_ha: Decimal
    collected_by: str
    collected_at: datetime
