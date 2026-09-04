import uuid


def _payload(**overrides) -> dict:
    return {
        "email": "procurement@kilang-tawau.example",
        "password": "mill-password-12",
        "role": "mill_user",
        **overrides,
    }


# --- Creation -------------------------------------------------------------


def test_admin_creates_a_mill_user(client, mill_id) -> None:
    response = client.post("/users", json=_payload(mill_id=str(mill_id)))

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "procurement@kilang-tawau.example"
    assert body["role"] == "mill_user"
    assert body["mill_id"] == str(mill_id)
    assert body["is_active"] is True
    assert "password" not in body and "password_hash" not in body


def test_admin_creates_another_admin(client) -> None:
    response = client.post("/users", json=_payload(role="admin", email="two@tapak.example"))

    assert response.status_code == 201
    assert response.json()["mill_id"] is None


def test_created_user_can_log_in(client, anon_client, mill_id) -> None:
    client.post("/users", json=_payload(mill_id=str(mill_id)))

    response = anon_client.post(
        "/auth/login",
        json={"email": "procurement@kilang-tawau.example", "password": "mill-password-12"},
    )

    assert response.status_code == 200


def test_email_is_stored_lowercased(client, mill_id) -> None:
    response = client.post(
        "/users", json=_payload(email="Procurement@Kilang-Tawau.Example", mill_id=str(mill_id))
    )

    assert response.json()["email"] == "procurement@kilang-tawau.example"


def test_duplicate_email_returns_409(client, mill_id) -> None:
    client.post("/users", json=_payload(mill_id=str(mill_id)))

    response = client.post("/users", json=_payload(mill_id=str(mill_id)))

    assert response.status_code == 409


def test_duplicate_email_differing_only_in_case_returns_409(client, mill_id) -> None:
    client.post("/users", json=_payload(mill_id=str(mill_id)))

    response = client.post(
        "/users", json=_payload(email="PROCUREMENT@kilang-tawau.example", mill_id=str(mill_id))
    )

    assert response.status_code == 409


# --- The role/tenant invariant --------------------------------------------


def test_admin_bound_to_a_mill_returns_422(client, mill_id) -> None:
    response = client.post("/users", json=_payload(role="admin", mill_id=str(mill_id)))

    assert response.status_code == 422


def test_mill_user_without_a_mill_returns_422(client) -> None:
    response = client.post("/users", json=_payload())

    assert response.status_code == 422


def test_mill_user_for_an_unregistered_mill_returns_404(client) -> None:
    response = client.post("/users", json=_payload(mill_id=str(uuid.uuid4())))

    assert response.status_code == 404


def test_short_password_returns_422(client, mill_id) -> None:
    response = client.post("/users", json=_payload(password="short", mill_id=str(mill_id)))

    assert response.status_code == 422


def test_unknown_role_returns_422(client, mill_id) -> None:
    response = client.post("/users", json=_payload(role="superuser", mill_id=str(mill_id)))

    assert response.status_code == 422


# --- Listing and revocation -----------------------------------------------


def test_list_users_returns_every_account(client, mill_id) -> None:
    client.post("/users", json=_payload(mill_id=str(mill_id)))

    emails = [u["email"] for u in client.get("/users").json()]

    assert "analyst@tapak.example" in emails  # the admin_token fixture's own account
    assert "procurement@kilang-tawau.example" in emails


def test_list_users_can_be_filtered_by_mill(client, register_mill) -> None:
    mill_a, mill_b = register_mill(), register_mill(name="Kilang Sawit Sandakan")
    client.post("/users", json=_payload(email="a@kilang.example", mill_id=str(mill_a)))
    client.post("/users", json=_payload(email="b@kilang.example", mill_id=str(mill_b)))

    body = client.get("/users", params={"mill_id": str(mill_a)}).json()

    assert [u["email"] for u in body] == ["a@kilang.example"]


def test_deactivating_a_user_blocks_their_login(client, anon_client, mill_id) -> None:
    created = client.post("/users", json=_payload(mill_id=str(mill_id))).json()

    response = client.patch(f"/users/{created['id']}", json={"is_active": False})

    assert response.status_code == 200
    assert response.json()["is_active"] is False
    login = anon_client.post(
        "/auth/login",
        json={"email": "procurement@kilang-tawau.example", "password": "mill-password-12"},
    )
    assert login.status_code == 401


def test_reactivating_a_user_restores_their_login(client, anon_client, mill_id) -> None:
    created = client.post("/users", json=_payload(mill_id=str(mill_id))).json()
    client.patch(f"/users/{created['id']}", json={"is_active": False})

    client.patch(f"/users/{created['id']}", json={"is_active": True})

    login = anon_client.post(
        "/auth/login",
        json={"email": "procurement@kilang-tawau.example", "password": "mill-password-12"},
    )
    assert login.status_code == 200


def test_patching_an_unknown_user_returns_404(client) -> None:
    response = client.patch(f"/users/{uuid.uuid4()}", json={"is_active": False})

    assert response.status_code == 404
