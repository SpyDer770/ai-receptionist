import pytest

from ai_schemas import StructuredIntent
from ai_service import AIServiceError

FUTURE_DATE = "2027-01-15"


@pytest.fixture()
def set_ai(monkeypatch):
    """Makes the AI return a fixed StructuredIntent instead of calling Gemini."""
    def _set(**fields):
        def fake_interpret(message, current_date):
            return StructuredIntent(**fields)
        monkeypatch.setattr("routers.chat.interpret_message", fake_interpret)
    return _set


def chat(client, message="test message"):
    return client.post("/chat", json={"message": message})


def appointment_count(client):
    return len(client.get("/appointments").json())


def test_greeting(client, set_ai):
    set_ai(intent="greeting", ai_reply="Hello there!")
    response = chat(client)
    assert response.status_code == 200
    assert response.json()["intent"] == "greeting"
    assert response.json()["reply"] == "Hello there!"


def test_faq_uses_trusted_answer(client, set_ai):
    set_ai(intent="faq", ai_reply="We are open 24 hours, all week!")
    reply = chat(client).json()["reply"]
    assert "Monday to Saturday" in reply
    assert "24 hours" not in reply


def test_book_missing_fields_creates_nothing(client, set_ai):
    set_ai(intent="book_appointment", date=FUTURE_DATE, time="17:00",
           missing_fields=["customer_name", "phone"])
    body = chat(client).json()
    assert "your name" in body["reply"]
    assert body["appointment_id"] is None
    assert appointment_count(client) == 0


def test_book_complete_creates_appointment(client, set_ai):
    set_ai(intent="book_appointment", customer_name="Rahul Verma",
           phone="9123456789", date=FUTURE_DATE, time="11:00")
    body = chat(client).json()
    assert "booked" in body["reply"].lower()
    assert body["appointment_id"] is not None
    assert appointment_count(client) == 1


def test_book_conflicting_slot(client, set_ai):
    set_ai(intent="book_appointment", customer_name="Rahul Verma",
           phone="9123456789", date=FUTURE_DATE, time="11:00")
    chat(client)
    body = chat(client).json()
    assert "already booked" in body["reply"]
    assert body["appointment_id"] is None
    assert appointment_count(client) == 1


def test_book_with_malformed_date_from_ai(client, set_ai):
    # The AI claims nothing is missing but returns an unparseable date.
    set_ai(intent="book_appointment", customer_name="Rahul Verma",
           phone="9123456789", date="tomorrow", time="11:00")
    body = chat(client).json()
    assert "couldn't book" in body["reply"]
    assert appointment_count(client) == 0


def test_cancel_without_id_asks_for_it(client, set_ai):
    set_ai(intent="cancel_appointment", missing_fields=["appointment_id"])
    assert "appointment ID" in chat(client).json()["reply"]


def test_book_cancel_and_get_flow(client, set_ai):
    set_ai(intent="book_appointment", customer_name="Rahul Verma",
           phone="9123456789", date=FUTURE_DATE, time="11:00")
    appointment_id = chat(client).json()["appointment_id"]

    set_ai(intent="cancel_appointment", appointment_id=appointment_id)
    assert "has been cancelled" in chat(client).json()["reply"]

    set_ai(intent="get_appointment", appointment_id=appointment_id)
    assert "(cancelled)" in chat(client).json()["reply"]


def test_get_unknown_appointment(client, set_ai):
    set_ai(intent="get_appointment", appointment_id=999999)
    assert "not found" in chat(client).json()["reply"]


def test_unknown_intent(client, set_ai):
    set_ai(intent="unknown", ai_reply="Sorry, I can't help with that.")
    body = chat(client).json()
    assert body["intent"] == "unknown"
    assert appointment_count(client) == 0


def test_ai_failure_returns_502(client, monkeypatch):
    def boom(message, current_date):
        raise AIServiceError("simulated outage")
    monkeypatch.setattr("routers.chat.interpret_message", boom)
    assert chat(client).status_code == 502


def test_empty_message_rejected(client, monkeypatch):
    def must_not_run(message, current_date):
        raise AssertionError("AI should not be called for an empty message")
    monkeypatch.setattr("routers.chat.interpret_message", must_not_run)
    assert chat(client, "").status_code == 422


def test_latency_headers_present(client, set_ai):
    set_ai(intent="greeting", ai_reply="Hi")
    headers = chat(client).headers
    for name in ("x-latency-total-ms", "x-latency-ai-ms",
                 "x-latency-db-ms", "x-latency-other-ms"):
        assert name in headers