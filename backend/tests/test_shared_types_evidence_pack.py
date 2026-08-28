import uuid
from datetime import UTC, date, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from shared_types.enums import (
    DeforestationStatus,
    LandOwnershipStatus,
    LandType,
    MalaysiaState,
    NoMixingStatus,
)
from shared_types.evidence_pack import (
    Batch,
    BatchCreate,
    BatchPlot,
    BatchPlotCreate,
    EvidencePackAssembly,
    EvidencePackCreate,
    EvidencePackDeforestationEvidence,
    EvidencePackLegalityEvidence,
    EvidencePackPlotGeolocation,
    EvidencePackSupplier,
)


def test_no_mixing_status_has_exactly_two_values() -> None:
    assert {s.value for s in NoMixingStatus} == {"single_source", "mixed_sources"}


def _valid_batch_create_kwargs(**overrides) -> dict:
    kwargs = {
        "product_description": "Crude palm oil",
        "trade_name": "TAPAK CPO",
        "hs_code": "1511.10",
        "net_mass_kg": Decimal("20000.00"),
        "recipient_name": "Sabah Oil Mills Sdn Bhd",
        "recipient_postal_address": "Lot 5, Industrial Estate, 91000 Tawau, Sabah",
        "recipient_email": "procurement@sabahoilmills.example",
        "created_by": "Analyst Bakar",
        "plots": [{"plot_id": uuid.uuid4(), "harvest_date": date(2026, 2, 1)}],
    }
    kwargs.update(overrides)
    return kwargs


def test_batch_create_rejects_empty_plot_list() -> None:
    kwargs = _valid_batch_create_kwargs(plots=[])

    with pytest.raises(ValidationError):
        BatchCreate(**kwargs)


def test_batch_create_rejects_duplicate_plot_ids() -> None:
    plot_id = uuid.uuid4()
    kwargs = _valid_batch_create_kwargs(
        plots=[
            {"plot_id": plot_id, "harvest_date": date(2026, 2, 1)},
            {"plot_id": plot_id, "harvest_date": date(2026, 2, 2)},
        ]
    )

    with pytest.raises(ValidationError):
        BatchCreate(**kwargs)


def test_batch_create_accepts_distinct_plot_ids() -> None:
    batch = BatchCreate(**_valid_batch_create_kwargs())

    assert len(batch.plots) == 1


def test_batch_round_trips_through_model_dump_and_validate() -> None:
    original = Batch(
        id=uuid.uuid4(),
        mill_id=uuid.uuid4(),
        product_description="Crude palm oil",
        trade_name="TAPAK CPO",
        hs_code="1511.10",
        net_mass_kg=Decimal("20000.00"),
        recipient_name="Sabah Oil Mills Sdn Bhd",
        recipient_postal_address="Lot 5, Industrial Estate, 91000 Tawau, Sabah",
        recipient_email="procurement@sabahoilmills.example",
        no_mixing_status=NoMixingStatus.SINGLE_SOURCE,
        created_by="Analyst Bakar",
        created_at=datetime.now(UTC),
        plots=[
            BatchPlot(
                id=uuid.uuid4(),
                mill_id=uuid.uuid4(),
                batch_id=uuid.uuid4(),
                plot_id=uuid.uuid4(),
                harvest_date=date(2026, 2, 1),
            )
        ],
    )

    restored = Batch.model_validate(original.model_dump())

    assert restored == original


def test_evidence_pack_create_requires_generated_by() -> None:
    with pytest.raises(ValidationError):
        EvidencePackCreate()


def test_evidence_pack_assembly_round_trips_through_model_dump_and_validate() -> None:
    household_id = uuid.uuid4()
    plot_id = uuid.uuid4()
    original = EvidencePackAssembly(
        product_description="Crude palm oil",
        trade_name="TAPAK CPO",
        hs_code="1511.10",
        net_mass_kg=Decimal("20000.00"),
        country_of_production="Malaysia",
        plots=[
            EvidencePackPlotGeolocation(
                plot_id=plot_id,
                household_id=household_id,
                centroid_lat=Decimal("4.050000"),
                centroid_lon=Decimal("117.050000"),
                area_ha=Decimal("2.5000"),
                harvest_date=date(2026, 2, 1),
            )
        ],
        production_date_start=date(2026, 2, 1),
        production_date_end=date(2026, 2, 1),
        suppliers=[
            EvidencePackSupplier(
                household_id=household_id,
                name="Ahmad bin Ismail",
                postal_address="Lot 12, Jalan Kebun, 91000 Tawau, Sabah",
                email="ahmad.ismail@example.com",
                district="Tawau",
                state=MalaysiaState.SABAH,
            )
        ],
        recipient_name="Sabah Oil Mills Sdn Bhd",
        recipient_postal_address="Lot 5, Industrial Estate, 91000 Tawau, Sabah",
        recipient_email="procurement@sabahoilmills.example",
        deforestation_evidence=[
            EvidencePackDeforestationEvidence(
                plot_id=plot_id,
                status=DeforestationStatus.COMPLIANT,
                reviewed_by="GIS Specialist Tan",
                reviewed_at=datetime.now(UTC),
            )
        ],
        legality_evidence=[
            EvidencePackLegalityEvidence(
                household_id=household_id,
                land_type=LandType.NATIVE_TITLE,
                rule_version="sabah-sarawak-v1",
                status=LandOwnershipStatus.CLEARED,
                documents_collected=[],
            )
        ],
        no_mixing_status=NoMixingStatus.SINGLE_SOURCE,
    )

    restored = EvidencePackAssembly.model_validate(original.model_dump())

    assert restored == original


def test_batch_plot_create_requires_harvest_date() -> None:
    with pytest.raises(ValidationError):
        BatchPlotCreate(plot_id=uuid.uuid4())
