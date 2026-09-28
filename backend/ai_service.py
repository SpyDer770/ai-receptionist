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

SYSTEM_PROMPT = """You are an intent-extraction assistant for a receptionist system.
Your ONLY job is to read the user's message and output a single JSON object.
You must NEVER perform any action yourself. You only describe what the user wants.

Choose exactly one "intent" from this fixed list:
- greeting: casual hello/hi, no task requested
- faq: asking about hours, location, services, or general questions
- book_appointment: wants to schedule a new appointment
- cancel_appointment: wants to cancel an existing appointment
- get_appointment: wants to see/check an existing appointment
- collect_contact: is providing their name/phone with no other clear request
- unknown: anything unrelated to a receptionist's job

Output ONLY a JSON object with these exact fields (no extra text, no markdown fences):
{
  "intent": "<one of the intents above>",
  "customer_name": "<string or null>",
  "phone": "<string or null>",
  "date": "<YYYY-MM-DD or null, resolve relative dates like 'tomorrow' using the given current date>",
  "time": "<HH:MM 24-hour or null>",
  "purpose": "<string or null>",
  "appointment_id": "<integer or null, only if the user mentions a specific id>",
  "missing_fields": ["<list field names still needed for this intent, empty if none>"],
  "ai_reply": "<a short, friendly natural-language reply, or null if not needed>"
}

Rules:
- For book_appointment: customer_name, phone, date, and time are required. List any that are missing in "missing_fields".
- For cancel_appointment and get_appointment: appointment_id is required if the user doesn't clearly refer to "my most recent" or similar. List "appointment_id" in missing_fields if absent.
- For greeting, faq, and unknown: fill "ai_reply" with a short natural response. Do NOT invent specific business facts (hours, prices) — for faq, just acknowledge the question in ai_reply and leave other fields null; the backend will supply the real answer.
- Never guess a phone number, name, date, or id that was not stated or clearly implied.
- Output must be valid JSON and nothing else.
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