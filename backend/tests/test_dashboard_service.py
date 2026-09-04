import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from backend.db.models.evidence_pack import Batch, BatchPlot, EvidencePack
from backend.db.models.household import Household
from backend.db.models.plot import Plot
from backend.db.models.verification_engine import FieldVerificationCheck, YieldLicenceCheck
from backend.services.dashboard.service import compute_household_status, list_mill_dashboard
from shared_types.enums import FieldVerificationStatus, MillDashboardStatus, NoMixingStatus


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


def _make_batch(db_session, mill_id: uuid.UUID) -> Batch:
    batch = Batch(
        mill_id=mill_id,
        product_description="Crude palm oil",
        trade_name="TAPAK CPO",
        hs_code="1511.10",
        net_mass_kg=Decimal("20000.00"),
        recipient_name="Sabah Oil Mills Sdn Bhd",
        recipient_postal_address="Lot 5, Industrial Estate, 91000 Tawau, Sabah",
        recipient_email="procurement@sabahoilmills.example",
        no_mixing_status=NoMixingStatus.SINGLE_SOURCE,
        created_by="Analyst Bakar",
    )
    db_session.add(batch)
    db_session.commit()
    db_session.refresh(batch)
    return batch


def _make_batch_plot(
    db_session, mill_id: uuid.UUID, batch_id: uuid.UUID, plot_id: uuid.UUID
) -> BatchPlot:
    batch_plot = BatchPlot(
        mill_id=mill_id,
        batch_id=batch_id,
        plot_id=plot_id,
        harvest_date=datetime(2026, 2, 1).date(),
    )
    db_session.add(batch_plot)
    db_session.commit()
    return batch_plot


def _make_evidence_pack(
    db_session, mill_id: uuid.UUID, batch_id: uuid.UUID, generated_at: datetime | None = None
) -> EvidencePack:
    pack = EvidencePack(
        mill_id=mill_id,
        batch_id=batch_id,
        assembled_data={},
        geojson={"type": "FeatureCollection", "features": []},
        generated_by="Analyst Bakar",
    )
    if generated_at is not None:
        pack.generated_at = generated_at
    db_session.add(pack)
    db_session.commit()
    return pack


def _give_household_an_evidence_pack(
    db_session,
    mill_id: uuid.UUID,
    household_id: uuid.UUID,
    plot_id: uuid.UUID,
    generated_at: datetime | None = None,
) -> None:
    batch = _make_batch(db_session, mill_id)
    _make_batch_plot(db_session, mill_id, batch.id, plot_id)
    _make_evidence_pack(db_session, mill_id, batch.id, generated_at=generated_at)


# --- compute_household_status ------------------------------------------


def test_compute_household_status_is_pending_with_no_records(db_session, mill_id) -> None:
    household = _make_household(db_session, mill_id)

    assert (
        compute_household_status(db_session, mill_id, household.id) == MillDashboardStatus.PENDING
    )


def test_compute_household_status_is_cleared_with_evidence_pack(db_session, mill_id) -> None:
    household = _make_household(db_session, mill_id)
    plot = _make_plot(db_session, mill_id, household.id)
    _give_household_an_evidence_pack(db_session, mill_id, household.id, plot.id)

    assert (
        compute_household_status(db_session, mill_id, household.id) == MillDashboardStatus.CLEARED
    )


def test_compute_household_status_is_frozen_with_needs_review_field_verification_check(
    db_session, mill_id
) -> None:
    household = _make_household(db_session, mill_id)
    plot = _make_plot(db_session, mill_id, household.id)
    _make_field_verification_check(
        db_session, mill_id, plot.id, FieldVerificationStatus.NEEDS_REVIEW
    )

    assert compute_household_status(db_session, mill_id, household.id) == MillDashboardStatus.FROZEN


def test_compute_household_status_is_frozen_with_needs_review_yield_licence_check(
    db_session, mill_id
) -> None:
    household = _make_household(db_session, mill_id)
    _make_yield_licence_check(
        db_session, mill_id, household.id, FieldVerificationStatus.NEEDS_REVIEW
    )

    assert compute_household_status(db_session, mill_id, household.id) == MillDashboardStatus.FROZEN


def test_compute_household_status_frozen_takes_priority_over_cleared(db_session, mill_id) -> None:
    household = _make_household(db_session, mill_id)
    plot = _make_plot(db_session, mill_id, household.id)
    # Both conditions hold: an evidence pack already exists, but a later
    # re-check on the same plot has since come back needs_review.
    _give_household_an_evidence_pack(db_session, mill_id, household.id, plot.id)
    _make_field_verification_check(
        db_session, mill_id, plot.id, FieldVerificationStatus.NEEDS_REVIEW
    )

    assert compute_household_status(db_session, mill_id, household.id) == MillDashboardStatus.FROZEN


def test_compute_household_status_is_frozen_when_renewal_has_lapsed(db_session, mill_id) -> None:
    household = _make_household(db_session, mill_id)
    plot = _make_plot(db_session, mill_id, household.id)
    _give_household_an_evidence_pack(
        db_session,
        mill_id,
        household.id,
        plot.id,
        generated_at=datetime.now(UTC) - timedelta(days=400),
    )

    assert compute_household_status(db_session, mill_id, household.id) == MillDashboardStatus.FROZEN


def test_compute_household_status_is_cleared_just_before_renewal_due_date(
    db_session, mill_id
) -> None:
    household = _make_household(db_session, mill_id)
    plot = _make_plot(db_session, mill_id, household.id)
    _give_household_an_evidence_pack(
        db_session,
        mill_id,
        household.id,
        plot.id,
        generated_at=datetime.now(UTC) - timedelta(days=300),
    )

    assert (
        compute_household_status(db_session, mill_id, household.id) == MillDashboardStatus.CLEARED
    )


# --- list_mill_dashboard -------------------------------------------------


def test_list_mill_dashboard_scopes_by_mill_id(db_session, register_mill) -> None:
    mill_a = register_mill()
    mill_b = register_mill()
    household_a = _make_household(db_session, mill_a)
    _make_household(db_session, mill_b)

    results = list_mill_dashboard(db_session, mill_a)

    assert [household.id for household, _ in results] == [household_a.id]
