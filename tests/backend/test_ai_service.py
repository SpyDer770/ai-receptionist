import pytest

import ai_service
from ai_service import AIServiceError, interpret_message


def fake_provider(text):
    return lambda message, current_date: text


def test_valid_json_becomes_structured_intent(monkeypatch):
    monkeypatch.setattr(ai_service, "_call_ai_provider",
                        fake_provider('{"intent": "greeting", "ai_reply": "Hi"}'))
    result = interpret_message("hello", "2026-09-28")
    assert result.intent == "greeting"


def test_non_json_reply_is_rejected(monkeypatch):
    monkeypatch.setattr(ai_service, "_call_ai_provider",
                        fake_provider("Sure! I will book that for you."))
    with pytest.raises(AIServiceError):
        interpret_message("book me in", "2026-09-28")


def test_hallucinated_intent_is_rejected(monkeypatch):
    monkeypatch.setattr(ai_service, "_call_ai_provider",
                        fake_provider('{"intent": "delete_everything"}'))
    with pytest.raises(AIServiceError):
        interpret_message("wipe it all", "2026-09-28")


def test_wrong_field_type_is_rejected(monkeypatch):
    monkeypatch.setattr(ai_service, "_call_ai_provider",
                        fake_provider('{"intent": "get_appointment", "appointment_id": "abc"}'))
    with pytest.raises(AIServiceError):
        interpret_message("show it", "2026-09-28")