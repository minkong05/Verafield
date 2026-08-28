import uuid
from datetime import UTC, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from shared_types.enums import FieldVerificationStatus
from shared_types.national_integration import NationalSystemsLookup, NationalSystemsLookupCreate


def _valid_create_kwargs() -> dict:
    return {
        "mpob_licence_number": "MPOB-12345",
        "sims_transaction_volume_kg": Decimal("8000.00"),
        "regional_yield_benchmark_kg_per_ha": Decimal("4000.00"),
        "geosawit_mapping_exists": True,
        "geosawit_reference": "GEOSAWIT-REF-1",
        "emspo_certification_status": "registered",
        "looked_up_by": "Analyst Bakar",
    }


def test_national_systems_lookup_create_accepts_valid_payload() -> None:
    lookup = NationalSystemsLookupCreate(**_valid_create_kwargs())

    assert lookup.geosawit_reference == "GEOSAWIT-REF-1"


def test_national_systems_lookup_create_defaults_geosawit_reference_to_none() -> None:
    kwargs = _valid_create_kwargs()
    del kwargs["geosawit_reference"]

    lookup = NationalSystemsLookupCreate(**kwargs)

    assert lookup.geosawit_reference is None


def test_national_systems_lookup_create_rejects_non_positive_sims_transaction_volume() -> None:
    kwargs = _valid_create_kwargs()
    kwargs["sims_transaction_volume_kg"] = Decimal("0")

    with pytest.raises(ValidationError):
        NationalSystemsLookupCreate(**kwargs)


def test_national_systems_lookup_create_rejects_non_positive_yield_benchmark() -> None:
    kwargs = _valid_create_kwargs()
    kwargs["regional_yield_benchmark_kg_per_ha"] = Decimal("0")

    with pytest.raises(ValidationError):
        NationalSystemsLookupCreate(**kwargs)


def test_national_systems_lookup_round_trips_through_model_dump_and_validate() -> None:
    original = NationalSystemsLookup(
        id=uuid.uuid4(),
        mill_id=uuid.uuid4(),
        household_id=uuid.uuid4(),
        mpob_licence_number="MPOB-12345",
        sims_transaction_volume_kg=Decimal("8000.00"),
        declared_area_ha=Decimal("2.5000"),
        regional_yield_benchmark_kg_per_ha=Decimal("4000.00"),
        volume_yield_mismatch=False,
        geosawit_mapping_exists=True,
        geosawit_reference="GEOSAWIT-REF-1",
        emspo_certification_status="registered",
        status=FieldVerificationStatus.CLEARED,
        looked_up_by="Analyst Bakar",
        looked_up_at=datetime.now(UTC),
    )

    restored = NationalSystemsLookup.model_validate(original.model_dump())

    assert restored == original
