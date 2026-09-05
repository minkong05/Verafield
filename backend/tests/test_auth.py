import uuid
from datetime import UTC, datetime, timedelta

import jwt

from backend.services.auth import service

ADMIN_EMAIL = "analyst@tapak.example"
ADMIN_PASSWORD = "admin-password-12"


def _login(client, email=ADMIN_EMAIL, password=ADMIN_PASSWORD):
    return client.post("/auth/login", json={"email": email, "password": password})


# --- Login ----------------------------------------------------------------


def test_login_returns_a_bearer_token(anon_client, admin_user) -> None:
    response = _login(anon_client)

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert datetime.fromisoformat(body["expires_at"]) > datetime.now(UTC)


def test_login_is_case_insensitive_on_email(anon_client, admin_user) -> None:
    assert _login(anon_client, email="Analyst@TAPAK.example").status_code == 200


def test_wrong_password_unknown_email_and_deactivated_user_are_indistinguishable(
    anon_client, client, admin_user, mill_id, make_mill_user
) -> None:
    """Three different underlying causes, one response. Anything else is an
    account-enumeration oracle."""
    deactivated, _ = make_mill_user(mill_id, is_active=False)

    wrong_password = _login(anon_client, password="not-the-password")
    unknown_email = _login(anon_client, email="nobody@tapak.example")
    inactive = _login(anon_client, email=deactivated.email, password="mill-password-12")

    assert wrong_password.status_code == unknown_email.status_code == 401
    assert inactive.status_code == 401
    assert wrong_password.json() == unknown_email.json() == inactive.json()


def test_login_response_carries_the_bearer_challenge(anon_client, admin_user) -> None:
    response = _login(anon_client, password="not-the-password")

    assert response.headers["www-authenticate"] == "Bearer"


# --- Token handling -------------------------------------------------------


def test_a_token_from_login_authenticates(anon_client, admin_user) -> None:
    token = _login(anon_client).json()["access_token"]

    response = anon_client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["email"] == ADMIN_EMAIL
    assert response.json()["role"] == "admin"
    assert response.json()["mill_id"] is None


def test_me_never_exposes_the_password_hash(client) -> None:
    body = client.get("/auth/me").json()

    assert "password_hash" not in body
    assert "password" not in body


def test_a_garbage_token_is_refused(anon_client, admin_user) -> None:
    response = anon_client.get("/auth/me", headers={"Authorization": "Bearer nonsense"})

    assert response.status_code == 401


def test_a_token_signed_with_another_key_is_refused(anon_client, admin_user) -> None:
    forged = jwt.encode(
        {"sub": str(admin_user.id), "exp": datetime.now(UTC) + timedelta(hours=1)},
        "a-different-secret-that-is-long-enough-000000",
        algorithm="HS256",
    )

    response = anon_client.get("/auth/me", headers={"Authorization": f"Bearer {forged}"})

    assert response.status_code == 401


def test_an_expired_token_is_refused(anon_client, admin_user) -> None:
    settings = service.get_auth_settings()
    expired = jwt.encode(
        {"sub": str(admin_user.id), "exp": datetime.now(UTC) - timedelta(seconds=1)},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    response = anon_client.get("/auth/me", headers={"Authorization": f"Bearer {expired}"})

    assert response.status_code == 401


def test_a_token_for_a_deleted_user_is_refused(anon_client, admin_user) -> None:
    settings = service.get_auth_settings()
    orphan = jwt.encode(
        {"sub": str(uuid.uuid4()), "exp": datetime.now(UTC) + timedelta(hours=1)},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    response = anon_client.get("/auth/me", headers={"Authorization": f"Bearer {orphan}"})

    assert response.status_code == 401


def test_the_token_carries_no_role_or_mill_claim(admin_user) -> None:
    """Authorization is re-read from the database each request; duplicating it
    into the token would create a second source of truth that a deactivation
    or a mill reassignment could not update."""
    settings = service.get_auth_settings()
    token, _ = service.create_access_token(admin_user)

    claims = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])

    assert set(claims) == {"sub", "iat", "exp"}


# --- Password change ------------------------------------------------------


def test_change_password_then_login_with_the_new_one(anon_client, client, admin_user) -> None:
    response = client.post(
        "/auth/change-password",
        json={"current_password": ADMIN_PASSWORD, "new_password": "a-new-password-12"},
    )

    assert response.status_code == 204
    assert _login(anon_client, password="a-new-password-12").status_code == 200
    assert _login(anon_client, password=ADMIN_PASSWORD).status_code == 401


def test_change_password_with_the_wrong_current_password_is_refused(client) -> None:
    response = client.post(
        "/auth/change-password",
        json={"current_password": "not-the-password", "new_password": "a-new-password-12"},
    )

    assert response.status_code == 401


def test_change_password_rejects_a_short_new_password(client) -> None:
    response = client.post(
        "/auth/change-password",
        json={"current_password": ADMIN_PASSWORD, "new_password": "short"},
    )

    assert response.status_code == 422


def test_change_password_requires_authentication(anon_client) -> None:
    response = anon_client.post(
        "/auth/change-password",
        json={"current_password": ADMIN_PASSWORD, "new_password": "a-new-password-12"},
    )

    assert response.status_code == 401
