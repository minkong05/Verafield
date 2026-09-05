import uuid
from datetime import UTC, datetime
from decimal import Decimal

import pytest

from backend.db.models.household import Household
from backend.db.models.plot import Plot
from backend.services.gap_assessment.service import HouseholdNotFoundError
from backend.services.national_integration.service import (
    NationalSystemsLookupAlreadyExistsError,
    NationalSystemsLookupNotFoundError,
    create_national_systems_lookup,
    get_national_systems_lookup,
)
from shared_types.enums import FieldVerificationStatus
from shared_types.national_integration import NationalSystemsLookupCreate


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


def _lookup_payload(**overrides) -> NationalSystemsLookupCreate:
    kwargs = {
        "mpob_licence_number": "MPOB-12345",
        "sims_transaction_volume_kg": Decimal("8000.00"),
        "regional_yield_benchmark_kg_per_ha": Decimal("4000.00"),
        "geosawit_mapping_exists": True,
        "geosawit_reference": "GEOSAWIT-REF-1",
        "emspo_certification_status": "registered",
        "looked_up_by": "Analyst Bakar",
    }
    kwargs.update(overrides)
    return NationalSystemsLookupCreate(**kwargs)


def test_create_national_systems_lookup_snapshots_declared_area(db_session, mill_id) -> None:
    household = _make_household(db_session, mill_id)
    _make_plot(db_session, mill_id, household.id)

    lookup = create_national_systems_lookup(db_session, mill_id, household.id, _lookup_payload())

    assert lookup.declared_area_ha == Decimal("2.5000")


def test_create_national_systems_lookup_is_cleared_within_benchmark(db_session, mill_id) -> None:
    household = _make_household(db_session, mill_id)
    _make_plot(db_session, mill_id, household.id)

    # 8000 kg / 2.5 ha = 3200 kg/ha, well under 4000 * 1.5 = 6000 kg/ha.
    lookup = create_national_systems_lookup(db_session, mill_id, household.id, _lookup_payload())

    assert lookup.volume_yield_mismatch is False
    assert lookup.status == FieldVerificationStatus.CLEARED


def test_create_national_systems_lookup_needs_review_over_benchmark(db_session, mill_id) -> None:
    household = _make_household(db_session, mill_id)
    _make_plot(db_session, mill_id, household.id)

    # 20000 kg / 2.5 ha = 8000 kg/ha, over 4000 * 1.5 = 6000 kg/ha.
    lookup = create_national_systems_lookup(
        db_session,
        mill_id,
        household.id,
        _lookup_payload(sims_transaction_volume_kg=Decimal("20000.00")),
    )

    assert lookup.volume_yield_mismatch is True
    assert lookup.status == FieldVerificationStatus.NEEDS_REVIEW


def test_create_national_systems_lookup_with_no_plots_has_no_mismatch(db_session, mill_id) -> None:
    household = _make_household(db_session, mill_id)

    lookup = create_national_systems_lookup(db_session, mill_id, household.id, _lookup_payload())

    assert lookup.declared_area_ha == Decimal("0")
    assert lookup.volume_yield_mismatch is False
    assert lookup.status == FieldVerificationStatus.CLEARED


def test_create_national_systems_lookup_raises_for_unknown_household(db_session, mill_id) -> None:

    with pytest.raises(HouseholdNotFoundError):
        create_national_systems_lookup(db_session, mill_id, uuid.uuid4(), _lookup_payload())


def test_create_national_systems_lookup_raises_when_one_already_exists(db_session, mill_id) -> None:
    household = _make_household(db_session, mill_id)
    create_national_systems_lookup(db_session, mill_id, household.id, _lookup_payload())

    with pytest.raises(NationalSystemsLookupAlreadyExistsError):
        create_national_systems_lookup(db_session, mill_id, household.id, _lookup_payload())


def test_get_national_systems_lookup_raises_when_none_exists(db_session, mill_id) -> None:
    household = _make_household(db_session, mill_id)

    with pytest.raises(NationalSystemsLookupNotFoundError):
        get_national_systems_lookup(db_session, mill_id, household.id)


def test_get_national_systems_lookup_is_scoped_by_mill(db_session, register_mill) -> None:
    mill_a = register_mill()
    mill_b = register_mill()
    household = _make_household(db_session, mill_a)
    create_national_systems_lookup(db_session, mill_a, household.id, _lookup_payload())

    with pytest.raises(HouseholdNotFoundError):
        get_national_systems_lookup(db_session, mill_b, household.id)
