from datetime import date as Date, datetime, time as Time

from ai_schemas import StructuredIntent
from chat_schemas import ChatResponse
from exceptions import (
    AppointmentAlreadyCancelledError,
    AppointmentConflictError,
    AppointmentNotFoundError,
)
from faq_data import FAQ_ANSWER
from schemas import AppointmentCreate
from services import appointment_service
from pydantic import ValidationError


FIELD_PROMPTS = {
    "customer_name": "your name",
    "phone": "your phone number",
    "date": "the date you'd like",
    "time": "the time you'd like",
    "appointment_id": "the appointment ID",
}


def _missing_fields_message(missing_fields: list[str]) -> str:
    readable = [FIELD_PROMPTS.get(f, f) for f in missing_fields]
    if len(readable) == 1:
        joined = readable[0]
    else:
        joined = ", ".join(readable[:-1]) + " and " + readable[-1]
    return f"Could you please share {joined}?"


def _handle_book_appointment(intent: StructuredIntent) -> ChatResponse:
    if intent.missing_fields:
        return ChatResponse(
            reply=_missing_fields_message(intent.missing_fields),
            intent=intent.intent,
        )

    try:
        appointment_data = AppointmentCreate(
            customer_name=intent.customer_name,
            phone=intent.phone,
            date=Date.fromisoformat(intent.date),
            time=Time.fromisoformat(intent.time),
            purpose=intent.purpose,
        )
    except (ValidationError, ValueError) as e:
        return ChatResponse(
            reply=f"Sorry, I couldn't book that: {e}",
            intent=intent.intent,
        )

    try:
        created = appointment_service.create_appointment(appointment_data)
    except AppointmentConflictError as e:
        return ChatResponse(reply=str(e), intent=intent.intent)

    return ChatResponse(
        reply=(
            f"You're booked, {created['customer_name']}! "
            f"Appointment #{created['id']} on {created['date']} at {created['time']}."
        ),
        intent=intent.intent,
        appointment_id=created["id"],
    )


def _handle_cancel_appointment(intent: StructuredIntent) -> ChatResponse:
    if intent.appointment_id is None:
        return ChatResponse(
            reply=_missing_fields_message(["appointment_id"]),
            intent=intent.intent,
        )

    try:
        cancelled = appointment_service.cancel_appointment(intent.appointment_id)
    except AppointmentNotFoundError as e:
        return ChatResponse(reply=str(e), intent=intent.intent)
    except AppointmentAlreadyCancelledError as e:
        return ChatResponse(reply=str(e), intent=intent.intent)

    return ChatResponse(
        reply=f"Appointment #{cancelled['id']} has been cancelled.",
        intent=intent.intent,
        appointment_id=cancelled["id"],
    )


def _handle_get_appointment(intent: StructuredIntent) -> ChatResponse:
    if intent.appointment_id is None:
        return ChatResponse(
            reply=_missing_fields_message(["appointment_id"]),
            intent=intent.intent,
        )

    try:
        appointment = appointment_service.get_appointment(intent.appointment_id)
    except AppointmentNotFoundError as e:
        return ChatResponse(reply=str(e), intent=intent.intent)

    return ChatResponse(
        reply=(
            f"Appointment #{appointment['id']} for {appointment['customer_name']} "
            f"is on {appointment['date']} at {appointment['time']} "
            f"({appointment['status']})."
        ),
        intent=intent.intent,
        appointment_id=appointment["id"],
    )


def handle_intent(intent: StructuredIntent) -> ChatResponse:
    """
    The single entry point: takes a validated StructuredIntent and decides
    what to do, calling the trusted appointment_service for anything
    that touches the database. Never touches the database directly.
    """
    if intent.intent == "greeting":
        return ChatResponse(
            reply=intent.ai_reply or "Hello! How can I help you today?",
            intent=intent.intent,
        )

    if intent.intent == "faq":
        return ChatResponse(reply=FAQ_ANSWER, intent=intent.intent)

    if intent.intent == "book_appointment":
        return _handle_book_appointment(intent)

    if intent.intent == "cancel_appointment":
        return _handle_cancel_appointment(intent)

    if intent.intent == "get_appointment":
        return _handle_get_appointment(intent)

    if intent.intent == "collect_contact":
        return ChatResponse(
            reply=intent.ai_reply or "Got it, thank you!",
            intent=intent.intent,
        )

    # unknown
    return ChatResponse(
        reply=intent.ai_reply or "Sorry, I can only help with appointment-related requests.",
        intent=intent.intent,
    )