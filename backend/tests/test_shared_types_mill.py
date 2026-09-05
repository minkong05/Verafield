import uuid
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from shared_types.enums import MalaysiaState
from shared_types.mill import Mill, MillCreate

VALID_PAYLOAD = {
    "name": "Kilang Sawit Tawau",
    "mpob_licence_number": "MPOB-500123456",
    "postal_address": "KM 12, Jalan Apas, 91000 Tawau, Sabah",
    "email": "ops@kilang-tawau.example",
    "district": "Tawau",
    "state": "sabah",
}


def test_mill_create_accepts_a_valid_payload() -> None:
    mill = MillCreate(**VALID_PAYLOAD)

    assert mill.name == "Kilang Sawit Tawau"
    assert mill.mpob_licence_number == "MPOB-500123456"
    assert mill.state == MalaysiaState.SABAH


def test_mill_create_rejects_an_unknown_state() -> None:
    with pytest.raises(ValidationError):
        MillCreate(**{**VALID_PAYLOAD, "state": "johor"})


def test_mill_create_rejects_a_missing_licence_number() -> None:
    payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "mpob_licence_number"}

    with pytest.raises(ValidationError):
        MillCreate(**payload)


def test_mill_read_model_has_no_mill_id_field() -> None:
    """mills.id *is* the mill_id. This is the only schema in the package
    without a mill_id, and the absence is load-bearing, not an oversight."""
    assert "mill_id" not in Mill.model_fields
    assert "id" in Mill.model_fields


def test_mill_read_model_round_trips() -> None:
    now = datetime.now(UTC)
    mill = Mill(
        **VALID_PAYLOAD,
        id=uuid.uuid4(),
        is_active=True,
        created_at=now,
        updated_at=now,
    )

    assert mill.is_active is True
    assert mill.state == MalaysiaState.SABAH
