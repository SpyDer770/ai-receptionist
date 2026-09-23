from typing import Optional

from exceptions import (
    AppointmentAlreadyCancelledError,
    AppointmentConflictError,
    AppointmentNotFoundError,
)
from repositories import appointment_repository as repo
from schemas import AppointmentCreate


def create_appointment(data: AppointmentCreate) -> dict:
    date_str = data.date.isoformat()
    time_str = data.time.strftime("%H:%M")

    if repo.find_booked_at(date_str, time_str):
        raise AppointmentConflictError(
            f"The slot on {date_str} at {time_str} is already booked"
        )

    return repo.create(
        customer_name=data.customer_name,
        phone=data.phone,
        date=date_str,
        time=time_str,
        purpose=data.purpose,
    )


def get_appointment(appointment_id: int) -> dict:
    appointment = repo.get_by_id(appointment_id)
    if appointment is None:
        raise AppointmentNotFoundError(f"Appointment {appointment_id} not found")
    return appointment


def list_appointments(status: Optional[str] = None,
                      date: Optional[str] = None) -> list[dict]:
    return repo.list_all(status=status, date=date)


def cancel_appointment(appointment_id: int) -> dict:
    appointment = get_appointment(appointment_id)
    if appointment["status"] == "cancelled":
        raise AppointmentAlreadyCancelledError(
            f"Appointment {appointment_id} is already cancelled"
        )
    return repo.mark_cancelled(appointment_id)