import uuid
from datetime import UTC, datetime, timedelta

from backend.db.models.evidence_pack import EvidencePack
from backend.services.renewal.service import add_one_year


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


def _deforestation_check_payload(**overrides) -> dict:
    payload = {
        "forest_area_ha": "1.2",
        "tree_height_m": "8.0",
        "canopy_cover_pct": "40.0",
        "predominantly_agricultural_or_urban": False,
        "pre_2020_imagery_date": "2020-06-01",
        "post_2020_imagery_date": "2026-06-01",
        "forest_loss_detected": False,
        "reviewed_by": "GIS Specialist Tan",
    }
    payload.update(overrides)
    return payload


def _field_verification_check_payload(**overrides) -> dict:
    payload = {
        "gnss_checkin_lat": "4.050000",
        "gnss_checkin_lon": "117.050000",
        "gnss_checkin_at": "2026-01-15T09:10:00Z",
        "photo_lat": "4.050000",
        "photo_lon": "117.050000",
        "photo_taken_at": "2026-01-15T09:10:00Z",
        "title_area_ha": "2.5000",
        "recorded_by": "Officer Aiman",
    }
    payload.update(overrides)
    return payload


def _yield_licence_check_payload(**overrides) -> dict:
    payload = {
        "mpob_licensed_area_ha": "3.0000",
        "annual_output_kg": "10000.00",
        "regional_yield_benchmark_kg_per_ha": "4000.00",
        "recorded_by": "Analyst Bakar",
    }
    payload.update(overrides)
    return payload


def _land_ownership_assessment_payload(**overrides) -> dict:
    # Sabah + native_title + sabah_native_title is the seeded rule combination
    # that resolves to "cleared" (see test_rules_engine.py).
    payload = {
        "state": "sabah",
        "land_type": "native_title",
        "assessed_by": "Officer Aiman",
        "documents_collected": ["sabah_native_title"],
    }
    payload.update(overrides)
    return payload


def _clear_household(client, mill_id: uuid.UUID, household_id: str, plot_id: str) -> None:
    assert (
        client.post(
            f"/mills/{mill_id}/households/{household_id}/plots/{plot_id}/deforestation-check",
            json=_deforestation_check_payload(),
        ).status_code
        == 201
    )
    assert (
        client.post(
            f"/mills/{mill_id}/households/{household_id}/plots/{plot_id}/field-verification-check",
            json=_field_verification_check_payload(),
        ).status_code
        == 201
    )
    assert (
        client.post(
            f"/mills/{mill_id}/households/{household_id}/yield-licence-check",
            json=_yield_licence_check_payload(),
        ).status_code
        == 201
    )
    assert (
        client.post(
            f"/mills/{mill_id}/households/{household_id}/land-ownership-assessment",
            json=_land_ownership_assessment_payload(),
        ).status_code
        == 201
    )


def _batch_payload(plots: list[dict], **overrides) -> dict:
    payload = {
        "product_description": "Crude palm oil",
        "trade_name": "TAPAK CPO",
        "hs_code": "1511.10",
        "net_mass_kg": "20000.00",
        "recipient_name": "Sabah Oil Mills Sdn Bhd",
        "recipient_postal_address": "Lot 5, Industrial Estate, 91000 Tawau, Sabah",
        "recipient_email": "procurement@sabahoilmills.example",
        "created_by": "Analyst Bakar",
        "plots": plots,
    }
    payload.update(overrides)
    return payload


def _create_batch(client, mill_id: uuid.UUID, plots: list[dict]) -> str:
    response = client.post(f"/mills/{mill_id}/batches", json=_batch_payload(plots))
    assert response.status_code == 201
    return response.json()["id"]


def _create_evidence_pack(client, mill_id: uuid.UUID, batch_id: str) -> str:
    response = client.post(
        f"/mills/{mill_id}/batches/{batch_id}/evidence-pack",
        json={"generated_by": "Analyst Bakar"},
    )
    assert response.status_code == 201
    return response.json()["id"]


def _household_with_evidence_pack(client, mill_id: uuid.UUID) -> str:
    household_id = _create_household(client, mill_id)
    plot_id = _create_plot(client, mill_id, household_id)
    _clear_household(client, mill_id, household_id, plot_id)
    batch_id = _create_batch(client, mill_id, [{"plot_id": plot_id, "harvest_date": "2026-02-01"}])
    _create_evidence_pack(client, mill_id, batch_id)
    return household_id


def _age_household_evidence_pack(db_session, mill_id: uuid.UUID, generated_at: datetime) -> None:
    pack = db_session.query(EvidencePack).filter(EvidencePack.mill_id == mill_id).one()
    pack.generated_at = generated_at
    db_session.commit()


# --- single-household route -------------------------------------------------


def test_household_with_no_records_has_null_renewal_fields_and_not_lapsed(client, mill_id) -> None:
    household_id = _create_household(client, mill_id)

    response = client.get(f"/mills/{mill_id}/households/{household_id}/renewal-status")

    assert response.status_code == 200
    body = response.json()
    assert body["last_evidence_pack_generated_at"] is None
    assert body["renewal_due_at"] is None
    assert body["lapsed"] is False


def test_household_with_recent_evidence_pack_is_not_lapsed(client, mill_id) -> None:
    household_id = _household_with_evidence_pack(client, mill_id)

    response = client.get(f"/mills/{mill_id}/households/{household_id}/renewal-status")

    assert response.status_code == 200
    body = response.json()
    assert body["last_evidence_pack_generated_at"] is not None
    assert body["renewal_due_at"] is not None
    assert body["lapsed"] is False


def test_household_with_evidence_pack_past_due_date_is_lapsed(client, db_session, mill_id) -> None:
    household_id = _household_with_evidence_pack(client, mill_id)
    aged = datetime.now(UTC) - timedelta(days=400)
    _age_household_evidence_pack(db_session, mill_id, aged)

    response = client.get(f"/mills/{mill_id}/households/{household_id}/renewal-status")

    assert response.status_code == 200
    body = response.json()
    assert body["lapsed"] is True
    due_at = datetime.fromisoformat(body["renewal_due_at"].replace("Z", "+00:00"))
    assert due_at == add_one_year(aged)


def test_read_household_renewal_status_404s_for_unknown_household(client, mill_id) -> None:

    response = client.get(f"/mills/{mill_id}/households/{uuid.uuid4()}/renewal-status")

    assert response.status_code == 404


def test_read_household_renewal_status_404s_for_household_in_other_mill(
    client, register_mill
) -> None:
    mill_a = register_mill()
    mill_b = register_mill()
    household_id = _create_household(client, mill_a)

    response = client.get(f"/mills/{mill_b}/households/{household_id}/renewal-status")

    assert response.status_code == 404


# --- mill-wide list route ----------------------------------------------------


def test_mill_renewal_status_only_shows_own_mills_households(client, register_mill) -> None:
    mill_a = register_mill()
    mill_b = register_mill()
    household_a = _create_household(client, mill_a)
    _create_household(client, mill_b)

    response = client.get(f"/mills/{mill_a}/renewal-status")

    assert response.status_code == 200
    household_ids = {entry["household_id"] for entry in response.json()}
    assert household_ids == {household_a}


def test_empty_mill_renewal_status_returns_empty_list(client, mill_id) -> None:
    response = client.get(f"/mills/{mill_id}/renewal-status")

    assert response.status_code == 200
    assert response.json() == []


def test_unregistered_mill_renewal_status_returns_404(client) -> None:
    response = client.get(f"/mills/{uuid.uuid4()}/renewal-status")

    assert response.status_code == 404


def test_renewal_status_entry_shape(client, mill_id) -> None:
    household_id = _create_household(client, mill_id, name="Siti binti Yusof")

    response = client.get(f"/mills/{mill_id}/households/{household_id}/renewal-status")

    assert response.status_code == 200
    body = response.json()
    assert body.keys() == {
        "household_id",
        "mill_id",
        "name",
        "district",
        "last_evidence_pack_generated_at",
        "renewal_due_at",
        "lapsed",
    }
    assert body["mill_id"] == str(mill_id)
    assert body["name"] == "Siti binti Yusof"
    assert body["district"] == "Tawau"
