import uuid


def test_create_household_returns_201_with_household_shape(client) -> None:
    mill_id = uuid.uuid4()

    response = client.post(f"/mills/{mill_id}/households", json={"name": "Ahmad bin Ismail"})

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Ahmad bin Ismail"
    assert body["mill_id"] == str(mill_id)
    assert uuid.UUID(body["id"])
