import uuid
from datetime import UTC, date, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from shared_types.enums import DeforestationStatus, FieldVerificationStatus
from shared_types.verification_engine import (
    DeforestationCheck,
    DeforestationCheckCreate,
    FieldVerificationCheck,
    FieldVerificationCheckCreate,
    YieldLicenceCheck,
    YieldLicenceCheckCreate,
)


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


def test_field_verification_status_has_exactly_two_values() -> None:
    assert {s.value for s in FieldVerificationStatus} == {"cleared", "needs_review"}


def _valid_field_verification_create_kwargs() -> dict:
    return {
        "gnss_checkin_lat": Decimal("4.050000"),
        "gnss_checkin_lon": Decimal("117.050000"),
        "gnss_checkin_at": datetime.now(UTC),
        "photo_lat": Decimal("4.050000"),
        "photo_lon": Decimal("117.050000"),
        "photo_taken_at": datetime.now(UTC),
        "title_area_ha": Decimal("2.5000"),
        "recorded_by": "Officer Aiman",
    }


def test_field_verification_check_round_trips_through_model_dump_and_validate() -> None:
    original = FieldVerificationCheck(
        id=uuid.uuid4(),
        mill_id=uuid.uuid4(),
        plot_id=uuid.uuid4(),
        gnss_checkin_lat=Decimal("4.050000"),
        gnss_checkin_lon=Decimal("117.050000"),
        gnss_checkin_at=datetime.now(UTC),
        photo_lat=Decimal("4.050000"),
        photo_lon=Decimal("117.050000"),
        photo_taken_at=datetime.now(UTC),
        title_area_ha=Decimal("2.5000"),
        checkin_mismatch=False,
        photo_mismatch=False,
        area_mismatch=False,
        status=FieldVerificationStatus.CLEARED,
        recorded_by="Officer Aiman",
        recorded_at=datetime.now(UTC),
    )

    restored = FieldVerificationCheck.model_validate(original.model_dump())

    assert restored == original


def test_field_verification_check_create_rejects_latitude_out_of_range() -> None:
    kwargs = _valid_field_verification_create_kwargs()
    kwargs["gnss_checkin_lat"] = Decimal("91")

    with pytest.raises(ValidationError):
        FieldVerificationCheckCreate(**kwargs)


def _valid_yield_licence_create_kwargs() -> dict:
    return {
        "mpob_licensed_area_ha": Decimal("3.0000"),
        "annual_output_kg": Decimal("10000.00"),
        "regional_yield_benchmark_kg_per_ha": Decimal("4000.00"),
        "recorded_by": "Analyst Bakar",
    }


def test_yield_licence_check_round_trips_through_model_dump_and_validate() -> None:
    original = YieldLicenceCheck(
        id=uuid.uuid4(),
        mill_id=uuid.uuid4(),
        household_id=uuid.uuid4(),
        mpob_licensed_area_ha=Decimal("3.0000"),
        declared_area_ha=Decimal("2.5000"),
        annual_output_kg=Decimal("10000.00"),
        regional_yield_benchmark_kg_per_ha=Decimal("4000.00"),
        licence_mismatch=False,
        yield_mismatch=False,
        status=FieldVerificationStatus.CLEARED,
        recorded_by="Analyst Bakar",
        recorded_at=datetime.now(UTC),
    )

    restored = YieldLicenceCheck.model_validate(original.model_dump())

    assert restored == original


def test_yield_licence_check_create_rejects_non_positive_area() -> None:
    kwargs = _valid_yield_licence_create_kwargs()
    kwargs["mpob_licensed_area_ha"] = Decimal("0")

    with pytest.raises(ValidationError):
        YieldLicenceCheckCreate(**kwargs)
