import re
from datetime import date as Date, time as Time, datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

PHONE_PATTERN = re.compile(r"^\+?\d{10,15}$")


class AppointmentCreate(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=100)
    phone: str
    date: Date
    time: Time
    purpose: Optional[str] = Field(default=None, max_length=200)

    @field_validator("customer_name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 2:
            raise ValueError("customer_name must contain at least 2 characters")
        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        cleaned = re.sub(r"[\s\-()]", "", value)
        if not PHONE_PATTERN.match(cleaned):
            raise ValueError("phone must be 10-15 digits, optionally starting with +")
        return cleaned

    @field_validator("date")
    @classmethod
    def date_not_in_past(cls, value: Date) -> Date:
        if value < Date.today():
            raise ValueError("date cannot be in the past")
        return value


class AppointmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_name: str
    phone: str
    date: Date
    time: Time
    purpose: Optional[str]
    status: Literal["booked", "cancelled"]
    created_at: datetime