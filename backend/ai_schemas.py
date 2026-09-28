from typing import List, Literal, Optional

from pydantic import BaseModel

Intent = Literal[
    "greeting",
    "faq",
    "book_appointment",
    "cancel_appointment",
    "get_appointment",
    "collect_contact",
    "unknown",
]


class StructuredIntent(BaseModel):
    intent: Intent
    customer_name: Optional[str] = None
    phone: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    purpose: Optional[str] = None
    appointment_id: Optional[int] = None
    missing_fields: List[str] = []
    ai_reply: Optional[str] = None