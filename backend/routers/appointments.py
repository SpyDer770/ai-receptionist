from typing import Literal, Optional

from fastapi import APIRouter, HTTPException, Path, Query, status
from datetime import date as Date

from exceptions import (
    AppointmentAlreadyCancelledError,
    AppointmentConflictError,
    AppointmentNotFoundError,
)
from schemas import AppointmentCreate, AppointmentResponse
from services import appointment_service as service

router = APIRouter(prefix="/appointments", tags=["Appointments"])


@router.post("", response_model=AppointmentResponse,
             status_code=status.HTTP_201_CREATED)
def create_appointment(data: AppointmentCreate):
    try:
        return service.create_appointment(data)
    except AppointmentConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("", response_model=list[AppointmentResponse])
def list_appointments(
    status_filter: Optional[Literal["booked", "cancelled"]] = Query(
        default=None, alias="status"),
    date: Optional[Date] = Query(default=None),
):
    return service.list_appointments(
        status=status_filter,
        date=date.isoformat() if date else None,
    )


@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(appointment_id: int = Path(..., gt=0)):
    try:
        return service.get_appointment(appointment_id)
    except AppointmentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{appointment_id}", response_model=AppointmentResponse)
def cancel_appointment(appointment_id: int = Path(..., gt=0)):
    try:
        return service.cancel_appointment(appointment_id)
    except AppointmentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AppointmentAlreadyCancelledError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))