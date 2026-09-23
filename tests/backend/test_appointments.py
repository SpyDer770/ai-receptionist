FUTURE_DATE = "2027-01-15"


def make_appointment(**overrides):
    data = {
        "customer_name": "Test Customer",
        "phone": "9876500000",
        "date": FUTURE_DATE,
        "time": "10:00",
        "purpose": "Checkup",
    }
    data.update(overrides)
    return data


def test_create_appointment(client):
    response = client.post("/appointments", json=make_appointment())
    assert response.status_code == 201
    body = response.json()
    assert body["customer_name"] == "Test Customer"
    assert body["status"] == "booked"
    assert "id" in body


def test_get_appointment(client):
    created = client.post("/appointments", json=make_appointment()).json()

    response = client.get(f"/appointments/{created['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_list_appointments(client):
    client.post("/appointments", json=make_appointment(time="09:00"))
    client.post("/appointments", json=make_appointment(time="11:00"))

    response = client.get("/appointments")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_cancel_appointment(client):
    created = client.post("/appointments", json=make_appointment()).json()

    response = client.delete(f"/appointments/{created['id']}")

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"


def test_invalid_appointment_data(client):
    bad_data = make_appointment(phone="abc", customer_name="A")

    response = client.post("/appointments", json=bad_data)

    assert response.status_code == 422
    fields_with_errors = [err["loc"][-1] for err in response.json()["detail"]]
    assert "phone" in fields_with_errors
    assert "customer_name" in fields_with_errors


def test_get_nonexistent_appointment(client):
    response = client.get("/appointments/999999")

    assert response.status_code == 404