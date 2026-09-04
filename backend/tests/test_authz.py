"""The cross-cutting authorization matrix.

The Features 01-09 suites all run as an admin (see conftest's client fixture),
so this file is the only place the mill-user path is exercised. Each mill-scoped
router shape is checked against all four principals.
"""

import uuid

HOUSEHOLD_PAYLOAD = {
    "name": "Ahmad bin Ismail",
    "postal_address": "Lot 12, Jalan Kebun, 91000 Tawau, Sabah",
    "email": "ahmad.ismail@example.com",
    "district": "Tawau",
}
BATCH_PAYLOAD = {
    "product_description": "Crude palm oil",
    "trade_name": "CPO",
    "hs_code": "1511.10",
    "net_mass_kg": "20000.00",
    "recipient_name": "Rotterdam Refinery BV",
    "recipient_postal_address": "Havenstraat 1, Rotterdam",
    "recipient_email": "intake@rotterdam-refinery.example",
    "created_by": "Analyst Bakar",
    "plots": [],
}
ASSESSMENT_PAYLOAD = {
    "state": "sabah",
    "land_type": "native_title",
    "assessed_by": "Officer Aiman",
    "documents": [],
}


def _requests(client, mill: uuid.UUID) -> list:
    """One call per mill-scoped router shape, including the rules_engine
    outlier that carries its dependency per-route rather than router-wide."""
    return [
        client.post(f"/mills/{mill}/households", json=HOUSEHOLD_PAYLOAD),
        client.get(f"/mills/{mill}/dashboard"),
        client.get(f"/mills/{mill}/renewal-status"),
        client.post(f"/mills/{mill}/batches", json=BATCH_PAYLOAD),
        client.post(
            f"/mills/{mill}/households/{uuid.uuid4()}/land-ownership-assessment",
            json=ASSESSMENT_PAYLOAD,
        ),
        client.get(f"/mills/{mill}"),
    ]


# --- Anonymous ------------------------------------------------------------


def test_anonymous_is_refused_by_every_mill_scoped_route(anon_client, mill_id) -> None:
    for response in _requests(anon_client, mill_id):
        assert response.status_code == 401, response.request.url


def test_anonymous_is_refused_by_the_rules_lookup(anon_client) -> None:
    assert anon_client.get("/land-ownership-rules/sabah/native_title").status_code == 401


def test_anonymous_is_refused_by_the_admin_routes(anon_client) -> None:
    assert anon_client.get("/mills").status_code == 401
    assert anon_client.get("/users").status_code == 401


def test_health_stays_anonymous(anon_client) -> None:
    """CI's docker-build job asserts nothing but this."""
    response = anon_client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# --- Mill user, own mill --------------------------------------------------


def test_mill_user_is_never_refused_on_its_own_mill(mill_client, mill_id) -> None:
    """Every shape reaches its route body. Some then fail on their own request
    validation (an empty plot list, an unknown household) — that is the
    feature's business, not authorization's, so the assertion is about what
    authorization did, not what each endpoint decided afterwards."""
    client = mill_client(mill_id)

    for response in _requests(client, mill_id):
        assert response.status_code not in (401, 403), response.request.url


def test_mill_user_can_actually_act_on_its_own_mill(mill_client, mill_id) -> None:
    """The positive counterpart: refusing nothing is only meaningful if the
    permitted calls genuinely succeed."""
    client = mill_client(mill_id)

    created = client.post(f"/mills/{mill_id}/households", json=HOUSEHOLD_PAYLOAD)

    assert created.status_code == 201
    assert created.json()["mill_id"] == str(mill_id)
    assert client.get(f"/mills/{mill_id}/dashboard").status_code == 200
    assert client.get(f"/mills/{mill_id}").json()["id"] == str(mill_id)


def test_mill_user_may_read_the_rules_lookup(mill_client, mill_id) -> None:
    client = mill_client(mill_id)

    assert client.get("/land-ownership-rules/sabah/native_title").status_code == 200


# --- Mill user, someone else's mill ---------------------------------------


def test_mill_user_cannot_reach_another_registered_mill(mill_client, register_mill) -> None:
    own, other = register_mill(), register_mill(name="Kilang Sawit Sandakan")
    client = mill_client(own)

    for response in _requests(client, other):
        assert response.status_code == 403, response.request.url


def test_mill_user_cannot_distinguish_a_registered_mill_from_an_invented_one(
    mill_client, register_mill
) -> None:
    """The oracle assertion, and the reason authorize_mill refuses from the
    token before it consults the registry: if these two responses differed,
    anyone with an account could enumerate which mill ids are real."""
    own, other = register_mill(), register_mill(name="Kilang Sawit Sandakan")
    client = mill_client(own)

    registered = client.get(f"/mills/{other}/dashboard")
    invented = client.get(f"/mills/{uuid.uuid4()}/dashboard")

    assert registered.status_code == invented.status_code == 403
    assert registered.json() == invented.json()


def test_mill_user_cannot_use_the_admin_routes(mill_client, mill_id) -> None:
    client = mill_client(mill_id)

    assert client.get("/mills").status_code == 403
    assert client.post("/mills", json={}).status_code == 403
    assert client.get("/users").status_code == 403


# --- Admin ----------------------------------------------------------------


def test_admin_reaches_any_mill(client, register_mill) -> None:
    for mill in (register_mill(), register_mill(name="Kilang Sawit Sandakan")):
        assert client.get(f"/mills/{mill}/dashboard").status_code == 200


def test_admin_alone_sees_the_registered_versus_unregistered_distinction(client, mill_id) -> None:
    assert client.get(f"/mills/{mill_id}/dashboard").status_code == 200
    assert client.get(f"/mills/{uuid.uuid4()}/dashboard").status_code == 404


# --- Deactivation ---------------------------------------------------------


def test_deactivated_user_is_refused(client, mill_id, make_mill_user) -> None:
    """Revocation takes effect on the next request, not the next login, since
    get_current_user re-reads is_active rather than trusting a token claim."""
    user, token = make_mill_user(mill_id)
    authed = {"Authorization": f"Bearer {token}"}
    assert client.get(f"/mills/{mill_id}/dashboard", headers=authed).status_code == 200

    client.patch(f"/users/{user.id}", json={"is_active": False})

    assert client.get(f"/mills/{mill_id}/dashboard", headers=authed).status_code == 401


def test_mill_user_of_a_deactivated_mill_is_refused_but_admin_is_not(
    client, mill_id, mill_client
) -> None:
    mill_user_client = mill_client(mill_id)
    client.patch(f"/mills/{mill_id}", json={"is_active": False})

    assert mill_user_client.get(f"/mills/{mill_id}/dashboard").status_code == 403
    assert client.get(f"/mills/{mill_id}/dashboard").status_code == 200


# --- Structural guard -----------------------------------------------------


def _fill(path: str) -> str:
    for param in ("mill_id", "household_id", "plot_id", "batch_id", "user_id"):
        path = path.replace(f"{{{param}}}", str(uuid.uuid4()))
    return path.replace("{state}", "sabah").replace("{land_type}", "native_title")


def test_no_route_is_reachable_without_a_credential_except_health(anon_client) -> None:
    """Walks the live OpenAPI schema rather than a hand-maintained list, so a
    mill-scoped route added later without the dependency fails here instead of
    shipping silently unauthenticated. Router-level dependencies run before
    body validation, so an empty body is enough to reach the check."""
    paths = anon_client.app.openapi()["paths"]
    ungated = []

    for path, operations in paths.items():
        if path == "/health":
            continue
        for method in operations:
            if method == "post" and path == "/auth/login":
                continue  # the one route that must accept anonymous callers
            response = anon_client.request(method.upper(), _fill(path), json={})
            if response.status_code != 401:
                ungated.append(f"{method.upper()} {path} -> {response.status_code}")

    assert not ungated, f"reachable without a credential: {ungated}"


def test_the_guard_covers_every_route_the_app_exposes(anon_client) -> None:
    """Guards the guard: if the schema stopped listing routes, the test above
    would pass vacuously."""
    paths = anon_client.app.openapi()["paths"]

    assert len(paths) >= 24
    assert "/health" in paths
    assert any("{mill_id}" in p for p in paths)
