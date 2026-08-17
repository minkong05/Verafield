from decimal import Decimal

from backend.services.verification_engine.service import compute_status
from shared_types.enums import DeforestationStatus

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
