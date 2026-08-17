import uuid


def _create_household(client, mill_id: uuid.UUID, name: str = "Ahmad bin Ismail") -> str:
    response = client.post(f"/mills/{mill_id}/households", json={"name": name})
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


def test_create_plot_returns_201(client) -> None:
    mill_id = uuid.uuid4()
    household_id = _create_household(client, mill_id)

    response = client.post(
        f"/mills/{mill_id}/households/{household_id}/plots", json=_plot_payload()
    )

    assert response.status_code == 201
    body = response.json()
    assert body["household_id"] == household_id
    assert body["area_ha"] == "2.5000"


def test_create_plot_for_unknown_household_returns_404(client) -> None:
    mill_id = uuid.uuid4()

    response = client.post(
        f"/mills/{mill_id}/households/{uuid.uuid4()}/plots", json=_plot_payload()
    )

    assert response.status_code == 404


def test_list_plots_returns_all_plots_for_a_household(client) -> None:
    mill_id = uuid.uuid4()
    household_id = _create_household(client, mill_id)
    _create_plot(client, mill_id, household_id)
    _create_plot(client, mill_id, household_id)

    response = client.get(f"/mills/{mill_id}/households/{household_id}/plots")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_plots_for_household_with_no_plots_returns_empty_list(client) -> None:
    mill_id = uuid.uuid4()
    household_id = _create_household(client, mill_id)

    response = client.get(f"/mills/{mill_id}/households/{household_id}/plots")

    assert response.status_code == 200
    assert response.json() == []


def test_get_plot_for_unknown_plot_id_returns_404(client) -> None:
    mill_id = uuid.uuid4()
    household_id = _create_household(client, mill_id)

    response = client.get(f"/mills/{mill_id}/households/{household_id}/plots/{uuid.uuid4()}")

    assert response.status_code == 404


def test_plot_is_not_visible_to_a_different_mill(client) -> None:
    mill_a = uuid.uuid4()
    mill_b = uuid.uuid4()
    household_id = _create_household(client, mill_a)
    plot_id = _create_plot(client, mill_a, household_id)

    response = client.get(f"/mills/{mill_b}/households/{household_id}/plots/{plot_id}")

    assert response.status_code == 404


def test_create_deforestation_check_for_non_forest_plot_returns_compliant(client) -> None:
    mill_id = uuid.uuid4()
    household_id = _create_household(client, mill_id)
    plot_id = _create_plot(client, mill_id, household_id)

    response = client.post(
        f"/mills/{mill_id}/households/{household_id}/plots/{plot_id}/deforestation-check",
        json=_deforestation_check_payload(forest_area_ha="0.5", forest_loss_detected=True),
    )

    assert response.status_code == 201
    assert response.json()["status"] == "compliant"


def test_create_deforestation_check_for_forest_plot_with_loss_returns_non_compliant(
    client,
) -> None:
    mill_id = uuid.uuid4()
    household_id = _create_household(client, mill_id)
    plot_id = _create_plot(client, mill_id, household_id)

    response = client.post(
        f"/mills/{mill_id}/households/{household_id}/plots/{plot_id}/deforestation-check",
        json=_deforestation_check_payload(forest_loss_detected=True),
    )

    assert response.status_code == 201
    assert response.json()["status"] == "non_compliant"


def test_create_deforestation_check_for_forest_plot_without_loss_returns_compliant(
    client,
) -> None:
    mill_id = uuid.uuid4()
    household_id = _create_household(client, mill_id)
    plot_id = _create_plot(client, mill_id, household_id)

    response = client.post(
        f"/mills/{mill_id}/households/{household_id}/plots/{plot_id}/deforestation-check",
        json=_deforestation_check_payload(forest_loss_detected=False),
    )

    assert response.status_code == 201
    assert response.json()["status"] == "compliant"


def test_create_deforestation_check_with_inconclusive_review_returns_needs_review(client) -> None:
    mill_id = uuid.uuid4()
    household_id = _create_household(client, mill_id)
    plot_id = _create_plot(client, mill_id, household_id)

    response = client.post(
        f"/mills/{mill_id}/households/{household_id}/plots/{plot_id}/deforestation-check",
        json=_deforestation_check_payload(forest_loss_detected=True, review_inconclusive=True),
    )

    assert response.status_code == 201
    assert response.json()["status"] == "needs_review"


def test_create_deforestation_check_for_unknown_plot_returns_404(client) -> None:
    mill_id = uuid.uuid4()
    household_id = _create_household(client, mill_id)

    response = client.post(
        f"/mills/{mill_id}/households/{household_id}/plots/{uuid.uuid4()}/deforestation-check",
        json=_deforestation_check_payload(),
    )

    assert response.status_code == 404


def test_create_deforestation_check_twice_for_same_plot_returns_409(client) -> None:
    mill_id = uuid.uuid4()
    household_id = _create_household(client, mill_id)
    plot_id = _create_plot(client, mill_id, household_id)
    url = f"/mills/{mill_id}/households/{household_id}/plots/{plot_id}/deforestation-check"
    assert client.post(url, json=_deforestation_check_payload()).status_code == 201

    response = client.post(url, json=_deforestation_check_payload())

    assert response.status_code == 409


def test_create_deforestation_check_with_post_imagery_date_before_cutoff_returns_422(
    client,
) -> None:
    mill_id = uuid.uuid4()
    household_id = _create_household(client, mill_id)
    plot_id = _create_plot(client, mill_id, household_id)

    response = client.post(
        f"/mills/{mill_id}/households/{household_id}/plots/{plot_id}/deforestation-check",
        json=_deforestation_check_payload(post_2020_imagery_date="2020-12-31"),
    )

    assert response.status_code == 422


def test_create_deforestation_check_with_pre_imagery_date_after_cutoff_returns_422(
    client,
) -> None:
    mill_id = uuid.uuid4()
    household_id = _create_household(client, mill_id)
    plot_id = _create_plot(client, mill_id, household_id)

    response = client.post(
        f"/mills/{mill_id}/households/{household_id}/plots/{plot_id}/deforestation-check",
        json=_deforestation_check_payload(pre_2020_imagery_date="2021-01-01"),
    )

    assert response.status_code == 422


def test_get_deforestation_check_for_plot_with_none_returns_404(client) -> None:
    mill_id = uuid.uuid4()
    household_id = _create_household(client, mill_id)
    plot_id = _create_plot(client, mill_id, household_id)

    response = client.get(
        f"/mills/{mill_id}/households/{household_id}/plots/{plot_id}/deforestation-check"
    )

    assert response.status_code == 404


def test_deforestation_check_is_not_visible_to_a_different_mill(client) -> None:
    mill_a = uuid.uuid4()
    mill_b = uuid.uuid4()
    household_id = _create_household(client, mill_a)
    plot_id = _create_plot(client, mill_a, household_id)
    assert (
        client.post(
            f"/mills/{mill_a}/households/{household_id}/plots/{plot_id}/deforestation-check",
            json=_deforestation_check_payload(),
        ).status_code
        == 201
    )

    response = client.get(
        f"/mills/{mill_b}/households/{household_id}/plots/{plot_id}/deforestation-check"
    )

    assert response.status_code == 404
