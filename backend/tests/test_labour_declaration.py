import uuid
from datetime import UTC, datetime, timedelta


def _create_household(client, mill_id: uuid.UUID, name: str = "Ahmad bin Ismail") -> str:
    response = client.post(f"/mills/{mill_id}/households", json={"name": name})
    assert response.status_code == 201
    return response.json()["id"]


def test_create_labour_declaration_returns_201(client) -> None:
    mill_id = uuid.uuid4()
    household_id = _create_household(client, mill_id)

    response = client.post(
        f"/mills/{mill_id}/households/{household_id}/labour-declaration",
        json={
            "labour_arrangement_description": "Family-run smallholding, no hired labour",
            "no_child_labour_confirmed": True,
            "has_land_dispute": False,
            "signature_method": "thumbprint",
            "collected_by": "Officer Aiman",
            "collected_at": datetime.now(UTC).isoformat(),
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["household_id"] == household_id
    assert body["signature_method"] == "thumbprint"
    assert body["no_child_labour_confirmed"] is True


def test_create_labour_declaration_preserves_the_submitted_collected_at(client) -> None:
    mill_id = uuid.uuid4()
    household_id = _create_household(client, mill_id)
    collected_at = datetime.now(UTC) - timedelta(days=3)

    response = client.post(
        f"/mills/{mill_id}/households/{household_id}/labour-declaration",
        json={
            "labour_arrangement_description": "Family-run smallholding, no hired labour",
            "no_child_labour_confirmed": True,
            "has_land_dispute": False,
            "signature_method": "signature",
            "collected_by": "Officer Aiman",
            "collected_at": collected_at.isoformat(),
        },
    )

    assert response.status_code == 201
    assert datetime.fromisoformat(response.json()["collected_at"]) == collected_at


def test_create_labour_declaration_missing_collected_at_returns_422(client) -> None:
    mill_id = uuid.uuid4()
    household_id = _create_household(client, mill_id)

    response = client.post(
        f"/mills/{mill_id}/households/{household_id}/labour-declaration",
        json={
            "labour_arrangement_description": "Family-run smallholding, no hired labour",
            "no_child_labour_confirmed": True,
            "has_land_dispute": False,
            "signature_method": "signature",
            "collected_by": "Officer Aiman",
        },
    )

    assert response.status_code == 422


def test_create_labour_declaration_twice_for_same_household_returns_409(client) -> None:
    mill_id = uuid.uuid4()
    household_id = _create_household(client, mill_id)
    payload = {
        "labour_arrangement_description": "Family-run smallholding, no hired labour",
        "no_child_labour_confirmed": True,
        "has_land_dispute": False,
        "signature_method": "signature",
        "collected_by": "Officer Aiman",
        "collected_at": datetime.now(UTC).isoformat(),
    }
    assert (
        client.post(
            f"/mills/{mill_id}/households/{household_id}/labour-declaration", json=payload
        ).status_code
        == 201
    )

    response = client.post(
        f"/mills/{mill_id}/households/{household_id}/labour-declaration", json=payload
    )

    assert response.status_code == 409


def test_create_labour_declaration_for_unknown_household_returns_404(client) -> None:
    mill_id = uuid.uuid4()

    response = client.post(
        f"/mills/{mill_id}/households/{uuid.uuid4()}/labour-declaration",
        json={
            "labour_arrangement_description": "Family-run smallholding, no hired labour",
            "no_child_labour_confirmed": True,
            "has_land_dispute": False,
            "signature_method": "signature",
            "collected_by": "Officer Aiman",
            "collected_at": datetime.now(UTC).isoformat(),
        },
    )

    assert response.status_code == 404


def test_get_labour_declaration_for_unknown_household_returns_404(client) -> None:
    mill_id = uuid.uuid4()

    response = client.get(f"/mills/{mill_id}/households/{uuid.uuid4()}/labour-declaration")

    assert response.status_code == 404


def test_labour_declaration_is_not_visible_to_a_different_mill(client) -> None:
    mill_a = uuid.uuid4()
    mill_b = uuid.uuid4()
    household_id = _create_household(client, mill_a)
    payload = {
        "labour_arrangement_description": "Family-run smallholding, no hired labour",
        "no_child_labour_confirmed": True,
        "has_land_dispute": False,
        "signature_method": "signature",
        "collected_by": "Officer Aiman",
        "collected_at": datetime.now(UTC).isoformat(),
    }
    assert (
        client.post(
            f"/mills/{mill_a}/households/{household_id}/labour-declaration", json=payload
        ).status_code
        == 201
    )

    response = client.get(f"/mills/{mill_b}/households/{household_id}/labour-declaration")

    assert response.status_code == 404


def test_create_consent_record_returns_201(client) -> None:
    mill_id = uuid.uuid4()
    household_id = _create_household(client, mill_id)

    response = client.post(
        f"/mills/{mill_id}/households/{household_id}/consent",
        json={
            "mykad_last4": "1234",
            "credit_referral_consent_given": True,
            "signature_method": "thumbprint",
            "collected_by": "Officer Aiman",
            "collected_at": datetime.now(UTC).isoformat(),
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["household_id"] == household_id
    assert body["mykad_last4"] == "1234"
    assert body["credit_referral_consent_given"] is True


def test_create_consent_record_defaults_credit_referral_consent_to_false(client) -> None:
    mill_id = uuid.uuid4()
    household_id = _create_household(client, mill_id)

    response = client.post(
        f"/mills/{mill_id}/households/{household_id}/consent",
        json={
            "mykad_last4": "1234",
            "signature_method": "signature",
            "collected_by": "Officer Aiman",
            "collected_at": datetime.now(UTC).isoformat(),
        },
    )

    assert response.status_code == 201
    assert response.json()["credit_referral_consent_given"] is False


def test_create_consent_record_with_invalid_mykad_last4_returns_422(client) -> None:
    mill_id = uuid.uuid4()
    household_id = _create_household(client, mill_id)
    base_payload = {
        "signature_method": "signature",
        "collected_by": "Officer Aiman",
        "collected_at": datetime.now(UTC).isoformat(),
    }

    for invalid_value in ("123", "12a4"):
        response = client.post(
            f"/mills/{mill_id}/households/{household_id}/consent",
            json={**base_payload, "mykad_last4": invalid_value},
        )
        assert response.status_code == 422


def test_create_consent_record_twice_for_same_household_returns_409(client) -> None:
    mill_id = uuid.uuid4()
    household_id = _create_household(client, mill_id)
    payload = {
        "mykad_last4": "1234",
        "signature_method": "signature",
        "collected_by": "Officer Aiman",
        "collected_at": datetime.now(UTC).isoformat(),
    }
    assert (
        client.post(f"/mills/{mill_id}/households/{household_id}/consent", json=payload).status_code
        == 201
    )

    response = client.post(f"/mills/{mill_id}/households/{household_id}/consent", json=payload)

    assert response.status_code == 409


def test_create_consent_record_for_unknown_household_returns_404(client) -> None:
    mill_id = uuid.uuid4()

    response = client.post(
        f"/mills/{mill_id}/households/{uuid.uuid4()}/consent",
        json={
            "mykad_last4": "1234",
            "signature_method": "signature",
            "collected_by": "Officer Aiman",
            "collected_at": datetime.now(UTC).isoformat(),
        },
    )

    assert response.status_code == 404


def test_get_consent_record_for_unknown_household_returns_404(client) -> None:
    mill_id = uuid.uuid4()

    response = client.get(f"/mills/{mill_id}/households/{uuid.uuid4()}/consent")

    assert response.status_code == 404


def test_consent_record_is_not_visible_to_a_different_mill(client) -> None:
    mill_a = uuid.uuid4()
    mill_b = uuid.uuid4()
    household_id = _create_household(client, mill_a)
    payload = {
        "mykad_last4": "1234",
        "signature_method": "signature",
        "collected_by": "Officer Aiman",
        "collected_at": datetime.now(UTC).isoformat(),
    }
    assert (
        client.post(f"/mills/{mill_a}/households/{household_id}/consent", json=payload).status_code
        == 201
    )

    response = client.get(f"/mills/{mill_b}/households/{household_id}/consent")

    assert response.status_code == 404
