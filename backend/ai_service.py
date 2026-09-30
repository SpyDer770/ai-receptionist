import json
import os

# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import ValidationError

from ai_schemas import StructuredIntent

load_dotenv()

_gemini_client: genai.Client | None = None

SYSTEM_PROMPT = """Extract structured intent from receptionist messages. Output ONLY JSON, no markdown, no extra text. Never perform actions yourself.

Intents: greeting (hi/hello), faq (hours/location/services), book_appointment (schedule new), cancel_appointment (cancel existing), get_appointment (check existing), collect_contact (only giving name/phone, no clear request), unknown (unrelated).

JSON shape:
{"intent": "<one of above>", "customer_name": string|null, "phone": string|null, "date": "YYYY-MM-DD"|null, "time": "HH:MM"|null, "purpose": string|null, "appointment_id": integer|null, "missing_fields": [string], "ai_reply": string|null}

Rules:
- book_appointment needs customer_name, phone, date, time — list missing ones in missing_fields. Resolve relative dates (e.g. "tomorrow") using the given current date.
- cancel_appointment/get_appointment need appointment_id — list it in missing_fields if absent.
- greeting/faq/unknown: fill ai_reply briefly. For faq, do not state specific hours/prices yourself — just acknowledge the question.
- Never invent a name, phone, date, or id not stated by the user.
"""


class AIServiceError(Exception):
    """Raised when the AI's response cannot be turned into a valid StructuredIntent."""


def _get_gemini_client() -> genai.Client:
    global _gemini_client
    if _gemini_client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise AIServiceError(
                "GEMINI_API_KEY is not set. Check your .env file."
            )
        _gemini_client = genai.Client(api_key=api_key)
    return _gemini_client


def _call_gemini(message: str, current_date: str) -> str:
    """Sends the message to Gemini and returns the raw text response."""
    model_name = os.getenv("AI_MODEL")
    if not model_name:
        raise AIServiceError("AI_MODEL is not set. Check your .env file.")

    client = _get_gemini_client()

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=f"Current date: {current_date}\nUser message: {message}",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0,
                response_mime_type="application/json",
            ),
        )
    except Exception as e:
        raise AIServiceError(f"AI request failed: {e}") from e

    if not response.text:
        raise AIServiceError("AI returned an empty response")

    return response.text


def _call_ai_provider(message: str, current_date: str) -> str:
    """Dispatches to the configured provider. Add new providers here later."""
    provider = os.getenv("AI_PROVIDER", "gemini").lower()

    if provider == "gemini":
        return _call_gemini(message, current_date)
    # Future: elif provider == "groq": return _call_groq(message, current_date)

    raise AIServiceError(f"Unsupported AI_PROVIDER: '{provider}'")


def interpret_message(message: str, current_date: str) -> StructuredIntent:
    """
    Sends the user's message to the configured AI provider and returns
    a validated StructuredIntent. Raises AIServiceError if the AI's output
    is missing, malformed, or invalid.
    """
    raw_text = _call_ai_provider(message, current_date)

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise AIServiceError(f"AI did not return valid JSON: {raw_text!r}") from e

    try:
        return StructuredIntent(**data)
    except ValidationError as e:
        raise AIServiceError(f"AI output failed schema validation: {e}") from e