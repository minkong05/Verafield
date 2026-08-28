import uuid
from datetime import UTC, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from shared_types.plot import Plot, PlotCreate


def _valid_polygon() -> list[list[float]]:
    return [[117.0, 4.0], [117.1, 4.0], [117.1, 4.1], [117.0, 4.1]]


def test_plot_round_trips_through_model_dump_and_validate() -> None:
    original = Plot(
        id=uuid.uuid4(),
        mill_id=uuid.uuid4(),
        household_id=uuid.uuid4(),
        polygon=_valid_polygon(),
        centroid_lat=Decimal("4.050000"),
        centroid_lon=Decimal("117.050000"),
        area_ha=Decimal("2.5000"),
        collected_by="Officer Aiman",
        collected_at=datetime.now(UTC),
    )

    restored = Plot.model_validate(original.model_dump())

    assert restored == original


def test_plot_create_rejects_polygon_with_fewer_than_three_points() -> None:
    with pytest.raises(ValidationError):
        PlotCreate(
            polygon=[[117.0, 4.0], [117.1, 4.0]],
            centroid_lat=Decimal("4.05"),
            centroid_lon=Decimal("117.05"),
            area_ha=Decimal("2.5"),
            collected_by="Officer Aiman",
            collected_at=datetime.now(UTC),
        )


def test_plot_create_rejects_polygon_point_that_is_not_a_lon_lat_pair() -> None:
    with pytest.raises(ValidationError):
        PlotCreate(
            polygon=[[117.0, 4.0, 0.0], [117.1, 4.0], [117.1, 4.1]],
            centroid_lat=Decimal("4.05"),
            centroid_lon=Decimal("117.05"),
            area_ha=Decimal("2.5"),
            collected_by="Officer Aiman",
            collected_at=datetime.now(UTC),
        )
