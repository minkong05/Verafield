import uuid

VALID_PAYLOAD = {
    "name": "Kilang Sawit Tawau",
    "mpob_licence_number": "MPOB-500123456",
    "postal_address": "KM 12, Jalan Apas, 91000 Tawau, Sabah",
    "email": "ops@kilang-tawau.example",
    "district": "Tawau",
    "state": "sabah",
}


def _register(client, **overrides) -> dict:
    response = client.post("/mills", json={**VALID_PAYLOAD, **overrides})
    assert response.status_code == 201, response.text
    return response.json()


# --- Registration ---------------------------------------------------------


def test_register_mill_returns_201_with_mill_shape(client) -> None:
    body = _register(client)

    assert uuid.UUID(body["id"])
    assert body["name"] == "Kilang Sawit Tawau"
    assert body["mpob_licence_number"] == "MPOB-500123456"
    assert body["district"] == "Tawau"
    assert body["state"] == "sabah"
    assert body["is_active"] is True
    assert "mill_id" not in body


def test_register_mill_with_a_duplicate_licence_returns_409(client) -> None:
    _register(client)

    response = client.post("/mills", json={**VALID_PAYLOAD, "name": "Kilang Sawit Sandakan"})

    assert response.status_code == 409


def test_register_mill_with_an_invalid_state_returns_422(client) -> None:
    response = client.post("/mills", json={**VALID_PAYLOAD, "state": "johor"})

    assert response.status_code == 422


# --- Lookup ---------------------------------------------------------------


def test_read_mill_returns_the_registered_mill(client) -> None:
    registered = _register(client)

    response = client.get(f"/mills/{registered['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == registered["id"]


def test_read_unregistered_mill_returns_404(client) -> None:
    response = client.get(f"/mills/{uuid.uuid4()}")

    assert response.status_code == 404


# --- The cross-cutting guard ----------------------------------------------
# One assertion per router shape: an unregistered mill must be refused before
# any household, plot, batch or evidence pack is touched.


def test_unregistered_mill_cannot_create_a_household(client) -> None:
    response = client.post(
        f"/mills/{uuid.uuid4()}/households",
        json={
            "name": "Ahmad bin Ismail",
            "postal_address": "Lot 12, Jalan Kebun, 91000 Tawau, Sabah",
            "email": "ahmad.ismail@example.com",
            "district": "Tawau",
        },
    )

    assert response.status_code == 404


def test_unregistered_mill_cannot_read_the_dashboard(client) -> None:
    assert client.get(f"/mills/{uuid.uuid4()}/dashboard").status_code == 404


def test_unregistered_mill_cannot_read_renewal_status(client) -> None:
    assert client.get(f"/mills/{uuid.uuid4()}/renewal-status").status_code == 404


def test_unregistered_mill_cannot_create_a_batch(client) -> None:
    response = client.post(
        f"/mills/{uuid.uuid4()}/batches",
        json={
            "product_description": "Crude palm oil",
            "trade_name": "CPO",
            "hs_code": "1511.10",
            "net_mass_kg": "20000.00",
            "recipient_name": "Rotterdam Refinery BV",
            "recipient_postal_address": "Havenstraat 1, Rotterdam",
            "recipient_email": "intake@rotterdam-refinery.example",
            "created_by": "Analyst Bakar",
            "plots": [],
        },
    )

    assert response.status_code == 404


def test_unregistered_mill_cannot_create_a_land_ownership_assessment(client) -> None:
    """rules_engine is the one router without a prefix, so it carries the
    dependency per-route rather than router-wide."""
    response = client.post(
        f"/mills/{uuid.uuid4()}/households/{uuid.uuid4()}/land-ownership-assessment",
        json={
            "state": "sabah",
            "land_type": "native_title",
            "assessed_by": "Officer Aiman",
            "documents": [],
        },
    )

    assert response.status_code == 404


def test_global_land_ownership_rules_route_stays_mill_free(client) -> None:
    """The rulebook is global reference data — it must not have picked up the
    mill dependency from its two mill-scoped siblings in the same router."""
    response = client.get("/land-ownership-rules/sabah/native_title")

    assert response.status_code == 200


# --- Who may register and enumerate (Feature 11) --------------------------


def test_registration_is_admin_only(mill_client, mill_id) -> None:
    """Admin-only registration is also what stops the duplicate-licence 409
    telling an outsider whether a licence is already held."""
    response = mill_client(mill_id).post("/mills", json=VALID_PAYLOAD)

    assert response.status_code == 403


def test_list_mills_returns_every_registered_mill_to_an_admin(client, register_mill) -> None:
    register_mill(name="Kilang Sawit Sandakan")
    register_mill(name="Kilang Sawit Lahad Datu")

    body = client.get("/mills").json()

    assert {"Kilang Sawit Sandakan", "Kilang Sawit Lahad Datu"} <= {m["name"] for m in body}


def test_list_mills_is_admin_only(mill_client, mill_id) -> None:
    """The route Feature 10 deliberately withheld until authentication
    existed: it enumerates the whole customer base."""
    assert mill_client(mill_id).get("/mills").status_code == 403


def test_mill_user_cannot_read_another_mill(mill_client, register_mill) -> None:
    own, other = register_mill(), register_mill(name="Kilang Sawit Sandakan")

    assert mill_client(own).get(f"/mills/{other}").status_code == 403


# --- Field-level update permissions ---------------------------------------


def test_mill_user_may_edit_its_own_contact_fields(mill_client, mill_id) -> None:
    response = mill_client(mill_id).patch(
        f"/mills/{mill_id}",
        json={
            "postal_address": "KM 20, Jalan Apas, 91000 Tawau, Sabah",
            "email": "new-ops@kilang-tawau.example",
            "district": "Semporna",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["postal_address"] == "KM 20, Jalan Apas, 91000 Tawau, Sabah"
    assert body["email"] == "new-ops@kilang-tawau.example"
    assert body["district"] == "Semporna"


def test_mill_user_may_not_change_its_own_licence_number(mill_client, mill_id) -> None:
    """The field this whole split exists for: mpob_licence_number is how
    Feature 08 resolves national-systems lookups, so a tenant must not be able
    to re-point its own compliance identity."""
    response = mill_client(mill_id).patch(
        f"/mills/{mill_id}", json={"mpob_licence_number": "MPOB-999999999"}
    )

    assert response.status_code == 403
    assert "mpob_licence_number" in response.json()["detail"]


def test_mill_user_may_not_change_name_state_or_activation(mill_client, mill_id) -> None:
    client = mill_client(mill_id)

    for field, value in [("name", "Renamed"), ("state", "sarawak"), ("is_active", False)]:
        assert client.patch(f"/mills/{mill_id}", json={field: value}).status_code == 403


def test_a_forbidden_field_is_refused_even_alongside_permitted_ones(mill_client, mill_id) -> None:
    """Partial application would be worse than refusal: the caller would be
    told nothing and half their edit would land."""
    response = mill_client(mill_id).patch(
        f"/mills/{mill_id}", json={"district": "Semporna", "name": "Renamed"}
    )

    assert response.status_code == 403


def test_admin_may_change_every_field(client, mill_id) -> None:
    response = client.patch(
        f"/mills/{mill_id}",
        json={
            "name": "Kilang Sawit Tawau Baharu",
            "mpob_licence_number": "MPOB-999999999",
            "state": "sarawak",
            "is_active": False,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Kilang Sawit Tawau Baharu"
    assert body["mpob_licence_number"] == "MPOB-999999999"
    assert body["state"] == "sarawak"
    assert body["is_active"] is False


def test_updating_to_an_already_held_licence_returns_409(client, register_mill) -> None:
    first = _register(client, mpob_licence_number="MPOB-111111111")
    second = register_mill(name="Kilang Sawit Sandakan")

    response = client.patch(f"/mills/{second}", json={"mpob_licence_number": "MPOB-111111111"})

    assert response.status_code == 409
    assert client.get(f"/mills/{first['id']}").json()["mpob_licence_number"] == "MPOB-111111111"


def test_an_empty_patch_changes_nothing(client, mill_id) -> None:
    before = client.get(f"/mills/{mill_id}").json()

    response = client.patch(f"/mills/{mill_id}", json={})

    assert response.status_code == 200
    assert response.json() == before


def test_an_explicit_null_does_not_blank_a_not_null_column(client, mill_id) -> None:
    """A null in a PATCH body means "leave alone", not "blank this out" —
    every Mill column is NOT NULL, so the alternative is a 500."""
    before = client.get(f"/mills/{mill_id}").json()

    response = client.patch(f"/mills/{mill_id}", json={"district": None})

    assert response.status_code == 200
    assert response.json()["district"] == before["district"]
