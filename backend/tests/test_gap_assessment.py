import uuid

from shared_types.enums import EvidenceCategory, GapStatus

FULL_CHECKLIST = [
    {"category": category.value, "status": GapStatus.PRESENT.value} for category in EvidenceCategory
]


def _create_household(client, mill_id: uuid.UUID, name: str = "Ahmad bin Ismail") -> str:
    response = client.post(f"/mills/{mill_id}/households", json={"name": name})
    assert response.status_code == 201
    return response.json()["id"]


def test_create_gap_assessment_with_full_checklist_returns_201(client) -> None:
    mill_id = uuid.uuid4()
    household_id = _create_household(client, mill_id)

    response = client.post(
        f"/mills/{mill_id}/households/{household_id}/gap-assessment",
        json={"assessed_by": "Officer Aiman", "items": FULL_CHECKLIST},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["household_id"] == household_id
    assert {item["category"] for item in body["items"]} == {c.value for c in EvidenceCategory}


def test_create_gap_assessment_twice_for_same_household_returns_409(client) -> None:
    mill_id = uuid.uuid4()
    household_id = _create_household(client, mill_id)
    payload = {"assessed_by": "Officer Aiman", "items": FULL_CHECKLIST}
    assert (
        client.post(
            f"/mills/{mill_id}/households/{household_id}/gap-assessment", json=payload
        ).status_code
        == 201
    )

    response = client.post(
        f"/mills/{mill_id}/households/{household_id}/gap-assessment", json=payload
    )

    assert response.status_code == 409


def test_create_gap_assessment_with_missing_category_returns_422(client) -> None:
    mill_id = uuid.uuid4()
    household_id = _create_household(client, mill_id)
    incomplete_items = FULL_CHECKLIST[:-1]  # drop one category

    response = client.post(
        f"/mills/{mill_id}/households/{household_id}/gap-assessment",
        json={"assessed_by": "Officer Aiman", "items": incomplete_items},
    )

    assert response.status_code == 422


def test_get_gap_assessment_for_unknown_household_returns_404(client) -> None:
    mill_id = uuid.uuid4()

    response = client.get(f"/mills/{mill_id}/households/{uuid.uuid4()}/gap-assessment")

    assert response.status_code == 404


def test_gap_assessment_is_not_visible_to_a_different_mill(client) -> None:
    mill_a = uuid.uuid4()
    mill_b = uuid.uuid4()
    household_id = _create_household(client, mill_a)
    payload = {"assessed_by": "Officer Aiman", "items": FULL_CHECKLIST}
    assert (
        client.post(
            f"/mills/{mill_a}/households/{household_id}/gap-assessment", json=payload
        ).status_code
        == 201
    )

    response = client.get(f"/mills/{mill_b}/households/{household_id}/gap-assessment")

    assert response.status_code == 404
