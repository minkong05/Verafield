import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from backend.db.models.evidence_pack import Batch, BatchPlot, EvidencePack
from backend.db.models.household import Household
from backend.db.models.plot import Plot
from backend.services.gap_assessment.service import HouseholdNotFoundError
from backend.services.renewal.service import (
    add_one_year,
    compute_renewal_due_at,
    get_household_renewal_status,
    get_latest_evidence_pack_generated_at,
    household_renewal_is_lapsed,
    list_mill_renewal_status,
)
from shared_types.enums import NoMixingStatus


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
    db_session.refresh(pack)
    return pack


def _give_household_an_evidence_pack(
    db_session,
    mill_id: uuid.UUID,
    household_id: uuid.UUID,
    plot_id: uuid.UUID,
    generated_at: datetime | None = None,
) -> EvidencePack:
    batch = _make_batch(db_session, mill_id)
    _make_batch_plot(db_session, mill_id, batch.id, plot_id)
    return _make_evidence_pack(db_session, mill_id, batch.id, generated_at=generated_at)


# --- add_one_year ----------------------------------------------------------


def test_add_one_year_advances_year_for_ordinary_date() -> None:
    assert add_one_year(datetime(2026, 3, 15, 10, 0, tzinfo=UTC)) == datetime(
        2027, 3, 15, 10, 0, tzinfo=UTC
    )


def test_add_one_year_preserves_time_of_day_and_timezone() -> None:
    assert add_one_year(datetime(2026, 6, 1, 14, 30, tzinfo=UTC)) == datetime(
        2027, 6, 1, 14, 30, tzinfo=UTC
    )


def test_add_one_year_from_feb_29_falls_back_to_mar_1_in_non_leap_target_year() -> None:
    # 2024 is a leap year, 2025 is not.
    assert add_one_year(datetime(2024, 2, 29, 9, 0, tzinfo=UTC)) == datetime(
        2025, 3, 1, 9, 0, tzinfo=UTC
    )


# --- get_latest_evidence_pack_generated_at ----------------------------------


def test_get_latest_evidence_pack_generated_at_returns_none_with_no_evidence_pack(
    db_session, mill_id
) -> None:
    household = _make_household(db_session, mill_id)

    assert get_latest_evidence_pack_generated_at(db_session, mill_id, household.id) is None


def test_get_latest_evidence_pack_generated_at_returns_generated_at_of_single_pack(
    db_session, mill_id
) -> None:
    household = _make_household(db_session, mill_id)
    plot = _make_plot(db_session, mill_id, household.id)
    generated_at = datetime(2025, 3, 1, 8, 0, tzinfo=UTC)
    pack = _give_household_an_evidence_pack(
        db_session, mill_id, household.id, plot.id, generated_at=generated_at
    )

    result = get_latest_evidence_pack_generated_at(db_session, mill_id, household.id)
    assert result == pack.generated_at


def test_get_latest_evidence_pack_generated_at_returns_max_across_multiple_batches(
    db_session, mill_id
) -> None:
    household = _make_household(db_session, mill_id)
    plot = _make_plot(db_session, mill_id, household.id)
    earlier = datetime(2025, 1, 1, 0, 0, tzinfo=UTC)
    later = datetime(2026, 6, 1, 0, 0, tzinfo=UTC)
    _give_household_an_evidence_pack(
        db_session, mill_id, household.id, plot.id, generated_at=earlier
    )
    _give_household_an_evidence_pack(db_session, mill_id, household.id, plot.id, generated_at=later)

    assert get_latest_evidence_pack_generated_at(db_session, mill_id, household.id) == later


def test_get_latest_evidence_pack_generated_at_is_scoped_by_mill(db_session, register_mill) -> None:
    mill_a = register_mill()
    mill_b = register_mill()
    household_a = _make_household(db_session, mill_a)
    plot_a = _make_plot(db_session, mill_a, household_a.id)
    _give_household_an_evidence_pack(db_session, mill_a, household_a.id, plot_a.id)

    assert get_latest_evidence_pack_generated_at(db_session, mill_b, household_a.id) is None


# --- compute_renewal_due_at --------------------------------------------------


def test_compute_renewal_due_at_is_none_with_no_evidence_pack(db_session, mill_id) -> None:
    household = _make_household(db_session, mill_id)

    assert compute_renewal_due_at(db_session, mill_id, household.id) is None


def test_compute_renewal_due_at_is_one_year_after_generated_at(db_session, mill_id) -> None:
    household = _make_household(db_session, mill_id)
    plot = _make_plot(db_session, mill_id, household.id)
    generated_at = datetime(2026, 5, 10, 12, 0, tzinfo=UTC)
    _give_household_an_evidence_pack(
        db_session, mill_id, household.id, plot.id, generated_at=generated_at
    )

    assert compute_renewal_due_at(db_session, mill_id, household.id) == datetime(
        2027, 5, 10, 12, 0, tzinfo=UTC
    )


def test_compute_renewal_due_at_leap_day_edge_case(db_session, mill_id) -> None:
    household = _make_household(db_session, mill_id)
    plot = _make_plot(db_session, mill_id, household.id)
    generated_at = datetime(2024, 2, 29, 7, 0, tzinfo=UTC)
    _give_household_an_evidence_pack(
        db_session, mill_id, household.id, plot.id, generated_at=generated_at
    )

    assert compute_renewal_due_at(db_session, mill_id, household.id) == datetime(
        2025, 3, 1, 7, 0, tzinfo=UTC
    )


# --- household_renewal_is_lapsed --------------------------------------------


def test_household_renewal_is_lapsed_is_false_with_no_evidence_pack(db_session, mill_id) -> None:
    household = _make_household(db_session, mill_id)

    assert household_renewal_is_lapsed(db_session, mill_id, household.id) is False


def test_household_renewal_is_lapsed_is_false_before_due_date(db_session, mill_id) -> None:
    household = _make_household(db_session, mill_id)
    plot = _make_plot(db_session, mill_id, household.id)
    generated_at = datetime(2026, 1, 1, 0, 0, tzinfo=UTC)
    _give_household_an_evidence_pack(
        db_session, mill_id, household.id, plot.id, generated_at=generated_at
    )
    due_at = add_one_year(generated_at)

    assert (
        household_renewal_is_lapsed(
            db_session, mill_id, household.id, as_of=due_at - timedelta(days=1)
        )
        is False
    )


def test_household_renewal_is_lapsed_is_false_one_microsecond_before_due_date(
    db_session, mill_id
) -> None:
    household = _make_household(db_session, mill_id)
    plot = _make_plot(db_session, mill_id, household.id)
    generated_at = datetime(2026, 1, 1, 0, 0, tzinfo=UTC)
    _give_household_an_evidence_pack(
        db_session, mill_id, household.id, plot.id, generated_at=generated_at
    )
    due_at = add_one_year(generated_at)

    assert (
        household_renewal_is_lapsed(
            db_session, mill_id, household.id, as_of=due_at - timedelta(microseconds=1)
        )
        is False
    )


def test_household_renewal_is_lapsed_is_true_exactly_at_due_date(db_session, mill_id) -> None:
    household = _make_household(db_session, mill_id)
    plot = _make_plot(db_session, mill_id, household.id)
    generated_at = datetime(2026, 1, 1, 0, 0, tzinfo=UTC)
    _give_household_an_evidence_pack(
        db_session, mill_id, household.id, plot.id, generated_at=generated_at
    )
    due_at = add_one_year(generated_at)

    assert household_renewal_is_lapsed(db_session, mill_id, household.id, as_of=due_at) is True


def test_household_renewal_is_lapsed_is_true_after_due_date(db_session, mill_id) -> None:
    household = _make_household(db_session, mill_id)
    plot = _make_plot(db_session, mill_id, household.id)
    generated_at = datetime(2026, 1, 1, 0, 0, tzinfo=UTC)
    _give_household_an_evidence_pack(
        db_session, mill_id, household.id, plot.id, generated_at=generated_at
    )
    due_at = add_one_year(generated_at)

    as_of = due_at + timedelta(days=1)
    assert household_renewal_is_lapsed(db_session, mill_id, household.id, as_of=as_of) is True


# --- get_household_renewal_status -------------------------------------------


def test_get_household_renewal_status_raises_for_unknown_household(db_session) -> None:
    with pytest.raises(HouseholdNotFoundError):
        get_household_renewal_status(db_session, uuid.uuid4(), uuid.uuid4())


def test_get_household_renewal_status_is_scoped_by_mill(db_session, register_mill) -> None:
    mill_a = register_mill()
    mill_b = register_mill()
    household_a = _make_household(db_session, mill_a)

    with pytest.raises(HouseholdNotFoundError):
        get_household_renewal_status(db_session, mill_b, household_a.id)


def test_get_household_renewal_status_with_no_evidence_pack_has_null_fields_and_not_lapsed(
    db_session, mill_id
) -> None:
    household = _make_household(db_session, mill_id)

    result = get_household_renewal_status(db_session, mill_id, household.id)

    assert result.last_evidence_pack_generated_at is None
    assert result.renewal_due_at is None
    assert result.lapsed is False


def test_get_household_renewal_status_reflects_due_date_and_lapsed_flag(
    db_session, mill_id
) -> None:
    household = _make_household(db_session, mill_id)
    plot = _make_plot(db_session, mill_id, household.id)
    generated_at = datetime(2024, 1, 1, 0, 0, tzinfo=UTC)
    _give_household_an_evidence_pack(
        db_session, mill_id, household.id, plot.id, generated_at=generated_at
    )

    result = get_household_renewal_status(
        db_session, mill_id, household.id, as_of=datetime(2027, 1, 1, tzinfo=UTC)
    )

    assert result.last_evidence_pack_generated_at == generated_at
    assert result.renewal_due_at == add_one_year(generated_at)
    assert result.lapsed is True


# --- list_mill_renewal_status ------------------------------------------------


def test_list_mill_renewal_status_scopes_by_mill_id(db_session, register_mill) -> None:
    mill_a = register_mill()
    mill_b = register_mill()
    household_a = _make_household(db_session, mill_a)
    _make_household(db_session, mill_b)

    results = list_mill_renewal_status(db_session, mill_a)

    assert [result.household.id for result in results] == [household_a.id]


def test_list_mill_renewal_status_includes_households_with_and_without_evidence_packs(
    db_session, mill_id
) -> None:
    pending_household = _make_household(db_session, mill_id)
    cleared_household = _make_household(db_session, mill_id)
    plot = _make_plot(db_session, mill_id, cleared_household.id)
    _give_household_an_evidence_pack(db_session, mill_id, cleared_household.id, plot.id)

    entries = list_mill_renewal_status(db_session, mill_id)
    results = {entry.household.id: entry for entry in entries}

    assert results[pending_household.id].renewal_due_at is None
    assert results[cleared_household.id].renewal_due_at is not None
