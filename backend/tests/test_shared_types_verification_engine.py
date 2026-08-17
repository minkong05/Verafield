import uuid
from datetime import UTC, date, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from shared_types.enums import DeforestationStatus
from shared_types.verification_engine import DeforestationCheck, DeforestationCheckCreate


def _valid_create_kwargs() -> dict:
    return {
        "forest_area_ha": Decimal("1.2"),
        "tree_height_m": Decimal("8.0"),
        "canopy_cover_pct": Decimal("40.0"),
        "predominantly_agricultural_or_urban": False,
        "pre_2020_imagery_date": date(2020, 6, 1),
        "post_2020_imagery_date": date(2026, 6, 1),
        "forest_loss_detected": False,
        "reviewed_by": "GIS Specialist Tan",
    }


def test_deforestation_status_has_exactly_three_values() -> None:
    assert {s.value for s in DeforestationStatus} == {
        "compliant",
        "non_compliant",
        "needs_review",
    }


def test_deforestation_check_round_trips_through_model_dump_and_validate() -> None:
    original = DeforestationCheck(
        id=uuid.uuid4(),
        mill_id=uuid.uuid4(),
        plot_id=uuid.uuid4(),
        forest_area_ha=Decimal("1.2000"),
        tree_height_m=Decimal("8.00"),
        canopy_cover_pct=Decimal("40.00"),
        predominantly_agricultural_or_urban=False,
        pre_2020_imagery_date=date(2020, 6, 1),
        post_2020_imagery_date=date(2026, 6, 1),
        forest_loss_detected=False,
        review_inconclusive=False,
        reviewed_by="GIS Specialist Tan",
        reviewed_at=datetime.now(UTC),
        status=DeforestationStatus.COMPLIANT,
    )

    restored = DeforestationCheck.model_validate(original.model_dump())

    assert restored == original


def test_deforestation_check_create_rejects_post_imagery_date_on_the_cutoff() -> None:
    kwargs = _valid_create_kwargs()
    kwargs["post_2020_imagery_date"] = date(2020, 12, 31)

    with pytest.raises(ValidationError):
        DeforestationCheckCreate(**kwargs)


def test_deforestation_check_create_rejects_pre_imagery_date_after_the_cutoff() -> None:
    kwargs = _valid_create_kwargs()
    kwargs["pre_2020_imagery_date"] = date(2021, 1, 1)

    with pytest.raises(ValidationError):
        DeforestationCheckCreate(**kwargs)


def test_deforestation_check_create_accepts_valid_imagery_dates() -> None:
    check = DeforestationCheckCreate(**_valid_create_kwargs())

    assert check.review_inconclusive is False
