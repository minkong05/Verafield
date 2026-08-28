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


def _plot_payload(**overrides) -> dict:
    payload = {
        "polygon": [[117.0, 4.0], [117.1, 4.0], [117.1, 4.1], [117.0, 4.1]],
        "centroid_lat": "4.050000",
        "centroid_lon": "117.050000",
        "area_ha": "2.5000",
        "collected_by": "Officer Aiman",
        "collected_at": "2026-01-15T09:00:00Z",
    }
    payload.update(overrides)
    return payload


def _create_plot(client, mill_id: uuid.UUID, household_id: str) -> str:
    response = client.post(
        f"/mills/{mill_id}/households/{household_id}/plots", json=_plot_payload()
    )
    assert response.status_code == 201
    return response.json()["id"]


def _national_systems_lookup_payload(**overrides) -> dict:
    payload = {
        "mpob_licence_number": "MPOB-12345",
        "sims_transaction_volume_kg": "8000.00",
        "regional_yield_benchmark_kg_per_ha": "4000.00",
        "geosawit_mapping_exists": True,
        "geosawit_reference": "GEOSAWIT-REF-1",
        "emspo_certification_status": "registered",
        "looked_up_by": "Analyst Bakar",
    }
    payload.update(overrides)
    return payload


def test_create_national_systems_lookup_within_benchmark_returns_cleared(client) -> None:
    mill_id = uuid.uuid4()
    household_id = _create_household(client, mill_id)
    _create_plot(client, mill_id, household_id)

    response = client.post(
        f"/mills/{mill_id}/households/{household_id}/national-systems-lookup",
        json=_national_systems_lookup_payload(),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "cleared"
    assert body["volume_yield_mismatch"] is False
    assert body["declared_area_ha"] == "2.5000"


def test_create_national_systems_lookup_over_benchmark_returns_needs_review(client) -> None:
    mill_id = uuid.uuid4()
    household_id = _create_household(client, mill_id)
    _create_plot(client, mill_id, household_id)

    response = client.post(
        f"/mills/{mill_id}/households/{household_id}/national-systems-lookup",
        json=_national_systems_lookup_payload(sims_transaction_volume_kg="20000.00"),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "needs_review"
    assert body["volume_yield_mismatch"] is True


def test_create_national_systems_lookup_for_unknown_household_returns_404(client) -> None:
    mill_id = uuid.uuid4()

    response = client.post(
        f"/mills/{mill_id}/households/{uuid.uuid4()}/national-systems-lookup",
        json=_national_systems_lookup_payload(),
    )

    assert response.status_code == 404


def test_create_national_systems_lookup_twice_for_same_household_returns_409(client) -> None:
    mill_id = uuid.uuid4()
    household_id = _create_household(client, mill_id)
    url = f"/mills/{mill_id}/households/{household_id}/national-systems-lookup"
    assert client.post(url, json=_national_systems_lookup_payload()).status_code == 201

    response = client.post(url, json=_national_systems_lookup_payload())

    assert response.status_code == 409


def test_get_national_systems_lookup_for_household_with_none_returns_404(client) -> None:
    mill_id = uuid.uuid4()
    household_id = _create_household(client, mill_id)

    response = client.get(f"/mills/{mill_id}/households/{household_id}/national-systems-lookup")

    assert response.status_code == 404


def test_get_national_systems_lookup_returns_created_lookup(client) -> None:
    mill_id = uuid.uuid4()
    household_id = _create_household(client, mill_id)
    url = f"/mills/{mill_id}/households/{household_id}/national-systems-lookup"
    created = client.post(url, json=_national_systems_lookup_payload()).json()

    response = client.get(url)

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_national_systems_lookup_is_not_visible_to_a_different_mill(client) -> None:
    mill_a = uuid.uuid4()
    mill_b = uuid.uuid4()
    household_id = _create_household(client, mill_a)
    client.post(
        f"/mills/{mill_a}/households/{household_id}/national-systems-lookup",
        json=_national_systems_lookup_payload(),
    )

    response = client.get(f"/mills/{mill_b}/households/{household_id}/national-systems-lookup")

    assert response.status_code == 404
