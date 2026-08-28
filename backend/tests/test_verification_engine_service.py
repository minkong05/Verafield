from decimal import Decimal

from backend.services.verification_engine.service import (
    _haversine_distance_m,
    compute_field_verification_status,
    compute_status,
    compute_yield_licence_status,
)
from shared_types.enums import DeforestationStatus, FieldVerificationStatus

_FOREST = {
    "forest_area_ha": Decimal("1"),
    "tree_height_m": Decimal("8"),
    "canopy_cover_pct": Decimal("40"),
    "predominantly_agricultural_or_urban": False,
}


def test_compute_status_returns_compliant_when_area_exactly_at_threshold() -> None:
    status = compute_status(
        forest_area_ha=Decimal("0.5"),
        tree_height_m=_FOREST["tree_height_m"],
        canopy_cover_pct=_FOREST["canopy_cover_pct"],
        predominantly_agricultural_or_urban=False,
        forest_loss_detected=True,
        review_inconclusive=False,
    )

    assert status == DeforestationStatus.COMPLIANT


def test_compute_status_returns_compliant_when_tree_height_exactly_at_threshold() -> None:
    status = compute_status(
        forest_area_ha=_FOREST["forest_area_ha"],
        tree_height_m=Decimal("5"),
        canopy_cover_pct=_FOREST["canopy_cover_pct"],
        predominantly_agricultural_or_urban=False,
        forest_loss_detected=True,
        review_inconclusive=False,
    )

    assert status == DeforestationStatus.COMPLIANT


def test_compute_status_returns_compliant_when_canopy_cover_exactly_at_threshold() -> None:
    status = compute_status(
        forest_area_ha=_FOREST["forest_area_ha"],
        tree_height_m=_FOREST["tree_height_m"],
        canopy_cover_pct=Decimal("10"),
        predominantly_agricultural_or_urban=False,
        forest_loss_detected=True,
        review_inconclusive=False,
    )

    assert status == DeforestationStatus.COMPLIANT


def test_compute_status_returns_compliant_when_predominantly_agricultural_or_urban() -> None:
    status = compute_status(
        **_FOREST | {"predominantly_agricultural_or_urban": True},
        forest_loss_detected=True,
        review_inconclusive=False,
    )

    assert status == DeforestationStatus.COMPLIANT


def test_compute_status_returns_non_compliant_when_forest_and_loss_detected() -> None:
    status = compute_status(**_FOREST, forest_loss_detected=True, review_inconclusive=False)

    assert status == DeforestationStatus.NON_COMPLIANT


def test_compute_status_returns_compliant_when_forest_and_no_loss_detected() -> None:
    status = compute_status(**_FOREST, forest_loss_detected=False, review_inconclusive=False)

    assert status == DeforestationStatus.COMPLIANT


def test_compute_status_returns_needs_review_when_inconclusive_even_with_loss_detected() -> None:
    status = compute_status(**_FOREST, forest_loss_detected=True, review_inconclusive=True)

    assert status == DeforestationStatus.NEEDS_REVIEW


def test_compute_status_returns_needs_review_when_inconclusive_even_without_loss_detected() -> None:
    status = compute_status(**_FOREST, forest_loss_detected=False, review_inconclusive=True)

    assert status == DeforestationStatus.NEEDS_REVIEW


def test_compute_field_verification_status_returns_cleared_when_no_mismatch() -> None:
    status = compute_field_verification_status(
        checkin_mismatch=False, photo_mismatch=False, area_mismatch=False
    )

    assert status == FieldVerificationStatus.CLEARED


def test_compute_field_verification_status_returns_needs_review_when_checkin_mismatch() -> None:
    status = compute_field_verification_status(
        checkin_mismatch=True, photo_mismatch=False, area_mismatch=False
    )

    assert status == FieldVerificationStatus.NEEDS_REVIEW


def test_compute_field_verification_status_returns_needs_review_when_photo_mismatch() -> None:
    status = compute_field_verification_status(
        checkin_mismatch=False, photo_mismatch=True, area_mismatch=False
    )

    assert status == FieldVerificationStatus.NEEDS_REVIEW


def test_compute_field_verification_status_returns_needs_review_when_area_mismatch() -> None:
    status = compute_field_verification_status(
        checkin_mismatch=False, photo_mismatch=False, area_mismatch=True
    )

    assert status == FieldVerificationStatus.NEEDS_REVIEW


def test_compute_yield_licence_status_returns_cleared_when_no_mismatch() -> None:
    status = compute_yield_licence_status(licence_mismatch=False, yield_mismatch=False)

    assert status == FieldVerificationStatus.CLEARED


def test_compute_yield_licence_status_returns_needs_review_when_licence_mismatch() -> None:
    status = compute_yield_licence_status(licence_mismatch=True, yield_mismatch=False)

    assert status == FieldVerificationStatus.NEEDS_REVIEW


def test_compute_yield_licence_status_returns_needs_review_when_yield_mismatch() -> None:
    status = compute_yield_licence_status(licence_mismatch=False, yield_mismatch=True)

    assert status == FieldVerificationStatus.NEEDS_REVIEW


def test_haversine_distance_between_identical_points_is_zero() -> None:
    distance = _haversine_distance_m(
        Decimal("4.05"), Decimal("117.05"), Decimal("4.05"), Decimal("117.05")
    )

    assert distance == Decimal("0")


def test_haversine_distance_matches_known_reference_value() -> None:
    # Same longitude, so the great-circle arc is exactly R * delta_latitude —
    # R=6,371,000m * 1 degree in radians = ~111,194.9m.
    distance = _haversine_distance_m(Decimal("0"), Decimal("0"), Decimal("1"), Decimal("0"))

    assert abs(distance - Decimal("111194.9")) < Decimal("1")
