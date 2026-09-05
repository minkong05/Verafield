import uuid


def test_create_household_returns_201_with_household_shape(client, mill_id) -> None:

    response = client.post(
        f"/mills/{mill_id}/households",
        json={
            "name": "Ahmad bin Ismail",
            "postal_address": "Lot 12, Jalan Kebun, 91000 Tawau, Sabah",
            "email": "ahmad.ismail@example.com",
            "district": "Tawau",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Ahmad bin Ismail"
    assert body["postal_address"] == "Lot 12, Jalan Kebun, 91000 Tawau, Sabah"
    assert body["email"] == "ahmad.ismail@example.com"
    assert body["district"] == "Tawau"
    assert body["mill_id"] == str(mill_id)
    assert uuid.UUID(body["id"])
