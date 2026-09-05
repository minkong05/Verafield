import uuid


def _create_household(client, mill_id: uuid.UUID, name: str = "Ahmad bin Ismail") -> str:
    response = client.post(
        f"/mills/{mill_id}/households",
        json={
            "name": name,
            "postal_address": "Lot 12, Jalan Kebun, 91000 Tawau, Sabah",
            "email": "ahmad.ismail@example.com",
            "district": "Tawau",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_read_land_document_rule_returns_required_documents(client) -> None:
    response = client.get("/land-ownership-rules/sabah/leased")

    assert response.status_code == 200
    body = response.json()
    assert body["state"] == "sabah"
    assert body["land_type"] == "leased"
    requirements = {r["document_type"]: r["is_hard_fail"] for r in body["requirements"]}
    assert requirements["tenancy_agreement"] is True
    assert requirements["landlord_identity"] is False


def test_read_land_document_rule_for_invalid_combination_returns_404(client) -> None:
    # native_title is a Sabah-only tenure type, no rule exists for Sarawak.
    response = client.get("/land-ownership-rules/sarawak/native_title")

    assert response.status_code == 404


def test_create_land_ownership_assessment_with_all_documents_returns_cleared(
    client, mill_id
) -> None:
    household_id = _create_household(client, mill_id)

    response = client.post(
        f"/mills/{mill_id}/households/{household_id}/land-ownership-assessment",
        json={
            "state": "sabah",
            "land_type": "leased",
            "assessed_by": "Officer Aiman",
            "documents_collected": ["tenancy_agreement", "landlord_identity", "landlord_title"],
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["household_id"] == household_id
    assert body["status"] == "cleared"
    assert body["rule_version"] == "sabah-sarawak-v1"


def test_create_land_ownership_assessment_missing_tenancy_agreement_returns_failed(
    client, mill_id
) -> None:
    household_id = _create_household(client, mill_id)

    response = client.post(
        f"/mills/{mill_id}/households/{household_id}/land-ownership-assessment",
        json={
            "state": "sabah",
            "land_type": "leased",
            "assessed_by": "Officer Aiman",
            "documents_collected": ["landlord_identity", "landlord_title"],
        },
    )

    assert response.status_code == 201
    assert response.json()["status"] == "failed"


def test_create_land_ownership_assessment_missing_non_hard_fail_document_needs_follow_up(
    client, mill_id
) -> None:
    household_id = _create_household(client, mill_id)

    response = client.post(
        f"/mills/{mill_id}/households/{household_id}/land-ownership-assessment",
        json={
            "state": "sabah",
            "land_type": "leased",
            "assessed_by": "Officer Aiman",
            "documents_collected": ["tenancy_agreement"],
        },
    )

    assert response.status_code == 201
    assert response.json()["status"] == "needs_follow_up"


def test_create_land_ownership_assessment_twice_for_same_household_returns_409(
    client, mill_id
) -> None:
    household_id = _create_household(client, mill_id)
    payload = {
        "state": "sabah",
        "land_type": "native_title",
        "assessed_by": "Officer Aiman",
        "documents_collected": ["sabah_native_title"],
    }
    assert (
        client.post(
            f"/mills/{mill_id}/households/{household_id}/land-ownership-assessment", json=payload
        ).status_code
        == 201
    )

    response = client.post(
        f"/mills/{mill_id}/households/{household_id}/land-ownership-assessment", json=payload
    )

    assert response.status_code == 409


def test_create_land_ownership_assessment_for_unknown_household_returns_404(
    client, mill_id
) -> None:

    response = client.post(
        f"/mills/{mill_id}/households/{uuid.uuid4()}/land-ownership-assessment",
        json={
            "state": "sabah",
            "land_type": "native_title",
            "assessed_by": "Officer Aiman",
            "documents_collected": ["sabah_native_title"],
        },
    )

    assert response.status_code == 404


def test_create_land_ownership_assessment_with_invalid_state_land_type_combination_returns_422(
    client, mill_id
) -> None:
    household_id = _create_household(client, mill_id)

    response = client.post(
        f"/mills/{mill_id}/households/{household_id}/land-ownership-assessment",
        json={
            "state": "sarawak",
            "land_type": "native_title",
            "assessed_by": "Officer Aiman",
            "documents_collected": [],
        },
    )

    assert response.status_code == 422


def test_get_land_ownership_assessment_for_unknown_household_returns_404(client, mill_id) -> None:

    response = client.get(f"/mills/{mill_id}/households/{uuid.uuid4()}/land-ownership-assessment")

    assert response.status_code == 404


def test_land_ownership_assessment_is_not_visible_to_a_different_mill(
    client, register_mill
) -> None:
    mill_a = register_mill()
    mill_b = register_mill()
    household_id = _create_household(client, mill_a)
    payload = {
        "state": "sabah",
        "land_type": "native_title",
        "assessed_by": "Officer Aiman",
        "documents_collected": ["sabah_native_title"],
    }
    assert (
        client.post(
            f"/mills/{mill_a}/households/{household_id}/land-ownership-assessment", json=payload
        ).status_code
        == 201
    )

    response = client.get(f"/mills/{mill_b}/households/{household_id}/land-ownership-assessment")

    assert response.status_code == 404
