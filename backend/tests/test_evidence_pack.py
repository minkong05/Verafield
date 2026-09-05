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


def _cleared_household_and_plot(client, mill_id: uuid.UUID) -> tuple[str, str]:
    household_id = _create_household(client, mill_id)
    plot_id = _create_plot(client, mill_id, household_id)
    _clear_household(client, mill_id, household_id, plot_id)
    return household_id, plot_id


# --- Batch creation -----------------------------------------------------


def test_create_batch_returns_201_with_batch_shape(client, mill_id) -> None:
    _, plot_id = _cleared_household_and_plot(client, mill_id)

    response = client.post(
        f"/mills/{mill_id}/batches",
        json=_batch_payload([{"plot_id": plot_id, "harvest_date": "2026-02-01"}]),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["product_description"] == "Crude palm oil"
    assert body["mill_id"] == str(mill_id)
    assert len(body["plots"]) == 1
    assert body["plots"][0]["plot_id"] == plot_id


def test_create_batch_computes_single_source_no_mixing_status_for_one_plot(client, mill_id) -> None:
    _, plot_id = _cleared_household_and_plot(client, mill_id)

    batch_id = _create_batch(client, mill_id, [{"plot_id": plot_id, "harvest_date": "2026-02-01"}])

    response = client.get(f"/mills/{mill_id}/batches/{batch_id}")
    assert response.json()["no_mixing_status"] == "single_source"


def test_create_batch_computes_mixed_sources_no_mixing_status_for_two_plots(
    client, mill_id
) -> None:
    household_id = _create_household(client, mill_id)
    plot_a = _create_plot(client, mill_id, household_id)
    plot_b = _create_plot(client, mill_id, household_id)

    batch_id = _create_batch(
        client,
        mill_id,
        [
            {"plot_id": plot_a, "harvest_date": "2026-02-01"},
            {"plot_id": plot_b, "harvest_date": "2026-02-02"},
        ],
    )

    response = client.get(f"/mills/{mill_id}/batches/{batch_id}")
    assert response.json()["no_mixing_status"] == "mixed_sources"


def test_create_batch_for_unknown_plot_returns_404(client, mill_id) -> None:

    response = client.post(
        f"/mills/{mill_id}/batches",
        json=_batch_payload([{"plot_id": str(uuid.uuid4()), "harvest_date": "2026-02-01"}]),
    )

    assert response.status_code == 404


def test_create_batch_rejects_duplicate_plot_ids_returns_422(client, mill_id) -> None:
    _, plot_id = _cleared_household_and_plot(client, mill_id)

    response = client.post(
        f"/mills/{mill_id}/batches",
        json=_batch_payload(
            [
                {"plot_id": plot_id, "harvest_date": "2026-02-01"},
                {"plot_id": plot_id, "harvest_date": "2026-02-02"},
            ]
        ),
    )

    assert response.status_code == 422


def test_create_batch_rejects_empty_plot_list_returns_422(client, mill_id) -> None:

    response = client.post(f"/mills/{mill_id}/batches", json=_batch_payload([]))

    assert response.status_code == 422


def test_get_batch_for_unknown_batch_returns_404(client, mill_id) -> None:

    response = client.get(f"/mills/{mill_id}/batches/{uuid.uuid4()}")

    assert response.status_code == 404


def test_batch_is_not_visible_to_a_different_mill(client, register_mill) -> None:
    mill_a = register_mill()
    mill_b = register_mill()
    _, plot_id = _cleared_household_and_plot(client, mill_a)
    batch_id = _create_batch(client, mill_a, [{"plot_id": plot_id, "harvest_date": "2026-02-01"}])

    response = client.get(f"/mills/{mill_b}/batches/{batch_id}")

    assert response.status_code == 404


# --- Evidence pack generation: the gate ----------------------------------


def test_generate_evidence_pack_returns_201_when_all_households_cleared(client, mill_id) -> None:
    _, plot_id = _cleared_household_and_plot(client, mill_id)
    batch_id = _create_batch(client, mill_id, [{"plot_id": plot_id, "harvest_date": "2026-02-01"}])

    response = client.post(
        f"/mills/{mill_id}/batches/{batch_id}/evidence-pack",
        json={"generated_by": "Analyst Bakar"},
    )

    assert response.status_code == 201


def test_generate_evidence_pack_blocked_when_a_plot_has_no_deforestation_check(
    client, mill_id
) -> None:
    household_id = _create_household(client, mill_id)
    plot_id = _create_plot(client, mill_id, household_id)
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
    batch_id = _create_batch(client, mill_id, [{"plot_id": plot_id, "harvest_date": "2026-02-01"}])

    response = client.post(
        f"/mills/{mill_id}/batches/{batch_id}/evidence-pack",
        json={"generated_by": "Analyst Bakar"},
    )

    assert response.status_code == 422


def test_generate_evidence_pack_blocked_when_a_plot_has_no_field_verification_check(
    client, mill_id
) -> None:
    household_id = _create_household(client, mill_id)
    plot_id = _create_plot(client, mill_id, household_id)
    assert (
        client.post(
            f"/mills/{mill_id}/households/{household_id}/plots/{plot_id}/deforestation-check",
            json=_deforestation_check_payload(),
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
    batch_id = _create_batch(client, mill_id, [{"plot_id": plot_id, "harvest_date": "2026-02-01"}])

    response = client.post(
        f"/mills/{mill_id}/batches/{batch_id}/evidence-pack",
        json={"generated_by": "Analyst Bakar"},
    )

    assert response.status_code == 422


def test_generate_evidence_pack_blocked_when_a_field_verification_check_is_needs_review(
    client, mill_id
) -> None:
    household_id = _create_household(client, mill_id)
    plot_id = _create_plot(client, mill_id, household_id)
    assert (
        client.post(
            f"/mills/{mill_id}/households/{household_id}/plots/{plot_id}/deforestation-check",
            json=_deforestation_check_payload(),
        ).status_code
        == 201
    )
    field_check = client.post(
        f"/mills/{mill_id}/households/{household_id}/plots/{plot_id}/field-verification-check",
        json=_field_verification_check_payload(gnss_checkin_lat="4.060000"),
    )
    assert field_check.status_code == 201
    assert field_check.json()["status"] == "needs_review"
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
    batch_id = _create_batch(client, mill_id, [{"plot_id": plot_id, "harvest_date": "2026-02-01"}])

    response = client.post(
        f"/mills/{mill_id}/batches/{batch_id}/evidence-pack",
        json={"generated_by": "Analyst Bakar"},
    )

    assert response.status_code == 422


def test_generate_evidence_pack_blocked_when_a_deforestation_check_is_needs_review(
    client, mill_id
) -> None:
    household_id = _create_household(client, mill_id)
    plot_id = _create_plot(client, mill_id, household_id)
    deforestation_check = client.post(
        f"/mills/{mill_id}/households/{household_id}/plots/{plot_id}/deforestation-check",
        json=_deforestation_check_payload(forest_loss_detected=True, review_inconclusive=True),
    )
    assert deforestation_check.status_code == 201
    assert deforestation_check.json()["status"] == "needs_review"
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
    batch_id = _create_batch(client, mill_id, [{"plot_id": plot_id, "harvest_date": "2026-02-01"}])

    response = client.post(
        f"/mills/{mill_id}/batches/{batch_id}/evidence-pack",
        json={"generated_by": "Analyst Bakar"},
    )

    assert response.status_code == 422


def test_generate_evidence_pack_blocked_when_yield_licence_check_is_missing(
    client, mill_id
) -> None:
    household_id = _create_household(client, mill_id)
    plot_id = _create_plot(client, mill_id, household_id)
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
            f"/mills/{mill_id}/households/{household_id}/land-ownership-assessment",
            json=_land_ownership_assessment_payload(),
        ).status_code
        == 201
    )
    batch_id = _create_batch(client, mill_id, [{"plot_id": plot_id, "harvest_date": "2026-02-01"}])

    response = client.post(
        f"/mills/{mill_id}/batches/{batch_id}/evidence-pack",
        json={"generated_by": "Analyst Bakar"},
    )

    assert response.status_code == 422


def test_generate_evidence_pack_blocked_when_land_ownership_assessment_is_missing(
    client, mill_id
) -> None:
    household_id = _create_household(client, mill_id)
    plot_id = _create_plot(client, mill_id, household_id)
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
    batch_id = _create_batch(client, mill_id, [{"plot_id": plot_id, "harvest_date": "2026-02-01"}])

    response = client.post(
        f"/mills/{mill_id}/batches/{batch_id}/evidence-pack",
        json={"generated_by": "Analyst Bakar"},
    )

    assert response.status_code == 422


def test_generate_evidence_pack_blocked_when_household_has_an_unrelated_uncleared_plot(
    client, mill_id
) -> None:
    household_id = _create_household(client, mill_id)
    plot_in_batch = _create_plot(client, mill_id, household_id)
    _clear_household(client, mill_id, household_id, plot_in_batch)
    # A second plot for the same household, not in the batch, with no checks at all.
    _create_plot(client, mill_id, household_id)
    batch_id = _create_batch(
        client, mill_id, [{"plot_id": plot_in_batch, "harvest_date": "2026-02-01"}]
    )

    response = client.post(
        f"/mills/{mill_id}/batches/{batch_id}/evidence-pack",
        json={"generated_by": "Analyst Bakar"},
    )

    assert response.status_code == 422


# --- Evidence pack generation: output shape and standard cases -----------


def test_generate_evidence_pack_assembled_data_maps_annex_ii_fields(client, mill_id) -> None:
    household_id, plot_id = _cleared_household_and_plot(client, mill_id)
    batch_id = _create_batch(client, mill_id, [{"plot_id": plot_id, "harvest_date": "2026-02-01"}])

    response = client.post(
        f"/mills/{mill_id}/batches/{batch_id}/evidence-pack",
        json={"generated_by": "Analyst Bakar"},
    )

    assert response.status_code == 201
    assembled = response.json()["assembled_data"]
    assert assembled["product_description"] == "Crude palm oil"
    assert assembled["trade_name"] == "TAPAK CPO"
    assert assembled["hs_code"] == "1511.10"
    assert assembled["net_mass_kg"] == "20000.00"
    assert assembled["country_of_production"] == "Malaysia"
    assert assembled["production_date_start"] == "2026-02-01"
    assert assembled["production_date_end"] == "2026-02-01"
    assert assembled["no_mixing_status"] == "single_source"

    [plot_entry] = assembled["plots"]
    assert plot_entry["plot_id"] == plot_id
    assert plot_entry["household_id"] == household_id
    assert plot_entry["area_ha"] == "2.5000"

    [supplier] = assembled["suppliers"]
    assert supplier["household_id"] == household_id
    assert supplier["name"] == "Ahmad bin Ismail"
    assert supplier["postal_address"] == "Lot 12, Jalan Kebun, 91000 Tawau, Sabah"
    assert supplier["email"] == "ahmad.ismail@example.com"
    assert supplier["district"] == "Tawau"
    assert supplier["state"] == "sabah"

    [deforestation_entry] = assembled["deforestation_evidence"]
    assert deforestation_entry["plot_id"] == plot_id
    assert deforestation_entry["status"] == "compliant"

    [legality_entry] = assembled["legality_evidence"]
    assert legality_entry["household_id"] == household_id
    assert legality_entry["status"] == "cleared"
    assert legality_entry["documents_collected"] == ["sabah_native_title"]


def test_generate_evidence_pack_geojson_has_one_feature_per_plot(client, mill_id) -> None:
    household_id = _create_household(client, mill_id)
    plot_a = _create_plot(client, mill_id, household_id)
    # plot_a is cleared (including the household-level yield-licence check)
    # before plot_b exists, so declared_area_ha is computed against plot_a
    # alone — matching _yield_licence_check_payload()'s baseline figures.
    _clear_household(client, mill_id, household_id, plot_a)
    plot_b = _create_plot(client, mill_id, household_id)
    assert (
        client.post(
            f"/mills/{mill_id}/households/{household_id}/plots/{plot_b}/deforestation-check",
            json=_deforestation_check_payload(),
        ).status_code
        == 201
    )
    assert (
        client.post(
            f"/mills/{mill_id}/households/{household_id}/plots/{plot_b}/field-verification-check",
            json=_field_verification_check_payload(),
        ).status_code
        == 201
    )
    batch_id = _create_batch(
        client,
        mill_id,
        [
            {"plot_id": plot_a, "harvest_date": "2026-02-01"},
            {"plot_id": plot_b, "harvest_date": "2026-02-02"},
        ],
    )

    response = client.post(
        f"/mills/{mill_id}/batches/{batch_id}/evidence-pack",
        json={"generated_by": "Analyst Bakar"},
    )

    assert response.status_code == 201
    geojson = response.json()["geojson"]
    assert geojson["type"] == "FeatureCollection"
    assert len(geojson["features"]) == 2


def test_generate_evidence_pack_for_unknown_batch_returns_404(client, mill_id) -> None:

    response = client.post(
        f"/mills/{mill_id}/batches/{uuid.uuid4()}/evidence-pack",
        json={"generated_by": "Analyst Bakar"},
    )

    assert response.status_code == 404


def test_generate_evidence_pack_twice_for_same_batch_returns_409(client, mill_id) -> None:
    _, plot_id = _cleared_household_and_plot(client, mill_id)
    batch_id = _create_batch(client, mill_id, [{"plot_id": plot_id, "harvest_date": "2026-02-01"}])
    url = f"/mills/{mill_id}/batches/{batch_id}/evidence-pack"
    assert client.post(url, json={"generated_by": "Analyst Bakar"}).status_code == 201

    response = client.post(url, json={"generated_by": "Analyst Bakar"})

    assert response.status_code == 409


def test_get_evidence_pack_for_batch_with_none_returns_404(client, mill_id) -> None:
    _, plot_id = _cleared_household_and_plot(client, mill_id)
    batch_id = _create_batch(client, mill_id, [{"plot_id": plot_id, "harvest_date": "2026-02-01"}])

    response = client.get(f"/mills/{mill_id}/batches/{batch_id}/evidence-pack")

    assert response.status_code == 404


def test_evidence_pack_is_not_visible_to_a_different_mill(client, register_mill) -> None:
    mill_a = register_mill()
    mill_b = register_mill()
    _, plot_id = _cleared_household_and_plot(client, mill_a)
    batch_id = _create_batch(client, mill_a, [{"plot_id": plot_id, "harvest_date": "2026-02-01"}])
    assert (
        client.post(
            f"/mills/{mill_a}/batches/{batch_id}/evidence-pack",
            json={"generated_by": "Analyst Bakar"},
        ).status_code
        == 201
    )

    response = client.get(f"/mills/{mill_b}/batches/{batch_id}/evidence-pack")

    assert response.status_code == 404
