import uuid
from datetime import UTC, datetime
from decimal import Decimal

from backend.db.models.household import Household
from backend.db.models.plot import Plot
from backend.db.models.rules_engine import LandDocumentRule, LandOwnershipAssessment
from backend.db.models.verification_engine import (
    DeforestationCheck,
    FieldVerificationCheck,
    YieldLicenceCheck,
)
from backend.services.evidence_pack.service import compute_no_mixing_status
from backend.services.verification_engine.service import household_is_cleared
from shared_types.enums import (
    DeforestationStatus,
    FieldVerificationStatus,
    LandOwnershipStatus,
    LandType,
    MalaysiaState,
)


def _make_household(db_session, mill_id: uuid.UUID) -> Household:
    household = Household(
        mill_id=mill_id,
        name="Ahmad bin Ismail",
        postal_address="Lot 12, Jalan Kebun, 91000 Tawau, Sabah",
        email="ahmad.ismail@example.com",
        district="Tawau",
    )
    db_session.add(household)
    db_session.commit()
    db_session.refresh(household)
    return household


def _make_plot(db_session, mill_id: uuid.UUID, household_id: uuid.UUID) -> Plot:
    plot = Plot(
        mill_id=mill_id,
        household_id=household_id,
        polygon=[[117.0, 4.0], [117.1, 4.0], [117.1, 4.1], [117.0, 4.1]],
        centroid_lat=Decimal("4.050000"),
        centroid_lon=Decimal("117.050000"),
        area_ha=Decimal("2.5000"),
        collected_by="Officer Aiman",
        collected_at=datetime(2026, 1, 15, 9, 0, tzinfo=UTC),
    )
    db_session.add(plot)
    db_session.commit()
    db_session.refresh(plot)
    return plot


def _make_deforestation_check(
    db_session, mill_id: uuid.UUID, plot_id: uuid.UUID, status: DeforestationStatus
) -> DeforestationCheck:
    check = DeforestationCheck(
        mill_id=mill_id,
        plot_id=plot_id,
        forest_area_ha=Decimal("1.2"),
        tree_height_m=Decimal("8.0"),
        canopy_cover_pct=Decimal("40.0"),
        predominantly_agricultural_or_urban=False,
        pre_2020_imagery_date=datetime(2020, 6, 1).date(),
        post_2020_imagery_date=datetime(2026, 6, 1).date(),
        forest_loss_detected=status == DeforestationStatus.NON_COMPLIANT,
        review_inconclusive=status == DeforestationStatus.NEEDS_REVIEW,
        reviewed_by="GIS Specialist Tan",
        status=status,
    )
    db_session.add(check)
    db_session.commit()
    return check


def _make_field_verification_check(
    db_session, mill_id: uuid.UUID, plot_id: uuid.UUID, status: FieldVerificationStatus
) -> FieldVerificationCheck:
    mismatch = status == FieldVerificationStatus.NEEDS_REVIEW
    check = FieldVerificationCheck(
        mill_id=mill_id,
        plot_id=plot_id,
        gnss_checkin_lat=Decimal("4.050000"),
        gnss_checkin_lon=Decimal("117.050000"),
        gnss_checkin_at=datetime(2026, 1, 15, 9, 10, tzinfo=UTC),
        photo_lat=Decimal("4.050000"),
        photo_lon=Decimal("117.050000"),
        photo_taken_at=datetime(2026, 1, 15, 9, 10, tzinfo=UTC),
        title_area_ha=Decimal("2.5000"),
        checkin_mismatch=mismatch,
        photo_mismatch=False,
        area_mismatch=False,
        status=status,
        recorded_by="Officer Aiman",
    )
    db_session.add(check)
    db_session.commit()
    return check


def _make_yield_licence_check(
    db_session, mill_id: uuid.UUID, household_id: uuid.UUID, status: FieldVerificationStatus
) -> YieldLicenceCheck:
    mismatch = status == FieldVerificationStatus.NEEDS_REVIEW
    check = YieldLicenceCheck(
        mill_id=mill_id,
        household_id=household_id,
        mpob_licensed_area_ha=Decimal("3.0000"),
        declared_area_ha=Decimal("2.5000"),
        annual_output_kg=Decimal("10000.00"),
        regional_yield_benchmark_kg_per_ha=Decimal("4000.00"),
        licence_mismatch=mismatch,
        yield_mismatch=False,
        status=status,
        recorded_by="Analyst Bakar",
    )
    db_session.add(check)
    db_session.commit()
    return check


def _get_seeded_rule(db_session, state: MalaysiaState, land_type: LandType) -> LandDocumentRule:
    return (
        db_session.query(LandDocumentRule)
        .filter(LandDocumentRule.state == state, LandDocumentRule.land_type == land_type)
        .one()
    )


def _make_land_ownership_assessment(
    db_session, mill_id: uuid.UUID, household_id: uuid.UUID, status: LandOwnershipStatus
) -> LandOwnershipAssessment:
    rule = _get_seeded_rule(db_session, MalaysiaState.SABAH, LandType.NATIVE_TITLE)
    assessment = LandOwnershipAssessment(
        mill_id=mill_id,
        household_id=household_id,
        state=MalaysiaState.SABAH,
        land_type=LandType.NATIVE_TITLE,
        rule_id=rule.id,
        status=status,
        assessed_by="Officer Aiman",
    )
    db_session.add(assessment)
    db_session.commit()
    return assessment


def _clear_household(
    db_session, mill_id: uuid.UUID, household_id: uuid.UUID, plot_id: uuid.UUID
) -> None:
    _make_deforestation_check(db_session, mill_id, plot_id, DeforestationStatus.COMPLIANT)
    _make_field_verification_check(db_session, mill_id, plot_id, FieldVerificationStatus.CLEARED)
    _make_yield_licence_check(db_session, mill_id, household_id, FieldVerificationStatus.CLEARED)
    _make_land_ownership_assessment(db_session, mill_id, household_id, LandOwnershipStatus.CLEARED)


def test_compute_no_mixing_status_returns_single_source_for_one_plot() -> None:
    plot_id = uuid.uuid4()

    assert compute_no_mixing_status([plot_id]).value == "single_source"


def test_compute_no_mixing_status_returns_mixed_sources_for_two_distinct_plots() -> None:
    status = compute_no_mixing_status([uuid.uuid4(), uuid.uuid4()])

    assert status.value == "mixed_sources"


def test_household_is_cleared_returns_true_when_all_checks_present_and_cleared(db_session) -> None:
    mill_id = uuid.uuid4()
    household = _make_household(db_session, mill_id)
    plot = _make_plot(db_session, mill_id, household.id)
    _clear_household(db_session, mill_id, household.id, plot.id)

    assert household_is_cleared(db_session, mill_id, household.id) is True


def test_household_is_cleared_returns_false_when_a_plot_has_no_deforestation_check(
    db_session,
) -> None:
    mill_id = uuid.uuid4()
    household = _make_household(db_session, mill_id)
    plot = _make_plot(db_session, mill_id, household.id)
    _make_field_verification_check(db_session, mill_id, plot.id, FieldVerificationStatus.CLEARED)
    _make_yield_licence_check(db_session, mill_id, household.id, FieldVerificationStatus.CLEARED)
    _make_land_ownership_assessment(db_session, mill_id, household.id, LandOwnershipStatus.CLEARED)

    assert household_is_cleared(db_session, mill_id, household.id) is False


def test_household_is_cleared_returns_false_when_a_plot_has_no_field_verification_check(
    db_session,
) -> None:
    mill_id = uuid.uuid4()
    household = _make_household(db_session, mill_id)
    plot = _make_plot(db_session, mill_id, household.id)
    _make_deforestation_check(db_session, mill_id, plot.id, DeforestationStatus.COMPLIANT)
    _make_yield_licence_check(db_session, mill_id, household.id, FieldVerificationStatus.CLEARED)
    _make_land_ownership_assessment(db_session, mill_id, household.id, LandOwnershipStatus.CLEARED)

    assert household_is_cleared(db_session, mill_id, household.id) is False


def test_household_is_cleared_returns_false_when_a_deforestation_check_is_needs_review(
    db_session,
) -> None:
    mill_id = uuid.uuid4()
    household = _make_household(db_session, mill_id)
    plot = _make_plot(db_session, mill_id, household.id)
    _make_deforestation_check(db_session, mill_id, plot.id, DeforestationStatus.NEEDS_REVIEW)
    _make_field_verification_check(db_session, mill_id, plot.id, FieldVerificationStatus.CLEARED)
    _make_yield_licence_check(db_session, mill_id, household.id, FieldVerificationStatus.CLEARED)
    _make_land_ownership_assessment(db_session, mill_id, household.id, LandOwnershipStatus.CLEARED)

    assert household_is_cleared(db_session, mill_id, household.id) is False


def test_household_is_cleared_returns_false_when_a_field_verification_check_is_needs_review(
    db_session,
) -> None:
    mill_id = uuid.uuid4()
    household = _make_household(db_session, mill_id)
    plot = _make_plot(db_session, mill_id, household.id)
    _make_deforestation_check(db_session, mill_id, plot.id, DeforestationStatus.COMPLIANT)
    _make_field_verification_check(
        db_session, mill_id, plot.id, FieldVerificationStatus.NEEDS_REVIEW
    )
    _make_yield_licence_check(db_session, mill_id, household.id, FieldVerificationStatus.CLEARED)
    _make_land_ownership_assessment(db_session, mill_id, household.id, LandOwnershipStatus.CLEARED)

    assert household_is_cleared(db_session, mill_id, household.id) is False


def test_household_is_cleared_returns_false_when_yield_licence_check_is_missing(db_session) -> None:
    mill_id = uuid.uuid4()
    household = _make_household(db_session, mill_id)
    plot = _make_plot(db_session, mill_id, household.id)
    _make_deforestation_check(db_session, mill_id, plot.id, DeforestationStatus.COMPLIANT)
    _make_field_verification_check(db_session, mill_id, plot.id, FieldVerificationStatus.CLEARED)
    _make_land_ownership_assessment(db_session, mill_id, household.id, LandOwnershipStatus.CLEARED)

    assert household_is_cleared(db_session, mill_id, household.id) is False


def test_household_is_cleared_returns_false_when_yield_licence_check_is_needs_review(
    db_session,
) -> None:
    mill_id = uuid.uuid4()
    household = _make_household(db_session, mill_id)
    plot = _make_plot(db_session, mill_id, household.id)
    _make_deforestation_check(db_session, mill_id, plot.id, DeforestationStatus.COMPLIANT)
    _make_field_verification_check(db_session, mill_id, plot.id, FieldVerificationStatus.CLEARED)
    _make_yield_licence_check(
        db_session, mill_id, household.id, FieldVerificationStatus.NEEDS_REVIEW
    )
    _make_land_ownership_assessment(db_session, mill_id, household.id, LandOwnershipStatus.CLEARED)

    assert household_is_cleared(db_session, mill_id, household.id) is False


def test_household_is_cleared_returns_false_when_land_ownership_assessment_is_missing(
    db_session,
) -> None:
    mill_id = uuid.uuid4()
    household = _make_household(db_session, mill_id)
    plot = _make_plot(db_session, mill_id, household.id)
    _make_deforestation_check(db_session, mill_id, plot.id, DeforestationStatus.COMPLIANT)
    _make_field_verification_check(db_session, mill_id, plot.id, FieldVerificationStatus.CLEARED)
    _make_yield_licence_check(db_session, mill_id, household.id, FieldVerificationStatus.CLEARED)

    assert household_is_cleared(db_session, mill_id, household.id) is False


def test_household_is_cleared_returns_false_when_land_ownership_assessment_is_not_cleared(
    db_session,
) -> None:
    mill_id = uuid.uuid4()
    household = _make_household(db_session, mill_id)
    plot = _make_plot(db_session, mill_id, household.id)
    _make_deforestation_check(db_session, mill_id, plot.id, DeforestationStatus.COMPLIANT)
    _make_field_verification_check(db_session, mill_id, plot.id, FieldVerificationStatus.CLEARED)
    _make_yield_licence_check(db_session, mill_id, household.id, FieldVerificationStatus.CLEARED)
    _make_land_ownership_assessment(
        db_session, mill_id, household.id, LandOwnershipStatus.NEEDS_FOLLOW_UP
    )

    assert household_is_cleared(db_session, mill_id, household.id) is False


def test_household_is_cleared_returns_false_when_one_of_two_plots_is_unresolved(db_session) -> None:
    mill_id = uuid.uuid4()
    household = _make_household(db_session, mill_id)
    plot_a = _make_plot(db_session, mill_id, household.id)
    _make_plot(db_session, mill_id, household.id)  # deliberately left with no checks at all
    _make_deforestation_check(db_session, mill_id, plot_a.id, DeforestationStatus.COMPLIANT)
    _make_field_verification_check(db_session, mill_id, plot_a.id, FieldVerificationStatus.CLEARED)
    _make_yield_licence_check(db_session, mill_id, household.id, FieldVerificationStatus.CLEARED)
    _make_land_ownership_assessment(db_session, mill_id, household.id, LandOwnershipStatus.CLEARED)

    assert household_is_cleared(db_session, mill_id, household.id) is False
