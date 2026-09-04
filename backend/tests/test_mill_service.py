import uuid

import pytest

from backend.services.mill import service
from shared_types.enums import MalaysiaState
from shared_types.mill import MillCreate


def _payload(licence: str = "MPOB-500123456", name: str = "Kilang Sawit Tawau") -> MillCreate:
    return MillCreate(
        name=name,
        mpob_licence_number=licence,
        postal_address="KM 12, Jalan Apas, 91000 Tawau, Sabah",
        email="ops@kilang-tawau.example",
        district="Tawau",
        state=MalaysiaState.SABAH,
    )


def test_create_mill_registers_a_mill(db_session) -> None:
    mill = service.create_mill(db_session, _payload())

    assert mill.id is not None
    assert mill.name == "Kilang Sawit Tawau"
    assert mill.state == MalaysiaState.SABAH
    assert mill.is_active is True


def test_create_mill_with_a_duplicate_licence_raises(db_session) -> None:
    service.create_mill(db_session, _payload())

    with pytest.raises(service.MillAlreadyExistsError):
        service.create_mill(db_session, _payload(name="Kilang Sawit Sandakan"))


def test_create_mill_allows_the_same_name_under_a_different_licence(db_session) -> None:
    first = service.create_mill(db_session, _payload(licence="MPOB-500000001"))
    second = service.create_mill(db_session, _payload(licence="MPOB-500000002"))

    assert first.id != second.id


def test_get_mill_returns_a_registered_mill(db_session) -> None:
    created = service.create_mill(db_session, _payload())

    assert service.get_mill(db_session, created.id).id == created.id


def test_get_mill_for_an_unregistered_id_raises(db_session) -> None:
    with pytest.raises(service.MillNotFoundError):
        service.get_mill(db_session, uuid.uuid4())


def test_list_mills_returns_every_registered_mill_by_name(db_session) -> None:
    service.create_mill(db_session, _payload(licence="MPOB-1", name="Zulkifli Mill"))
    service.create_mill(db_session, _payload(licence="MPOB-2", name="Ah Kau Mill"))

    assert [m.name for m in service.list_mills(db_session)] == ["Ah Kau Mill", "Zulkifli Mill"]
