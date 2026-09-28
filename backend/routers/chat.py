import logging
import time
from datetime import date as Date

from fastapi import APIRouter, HTTPException, Response, status

from ai_service import AIServiceError, interpret_message
from chat_schemas import ChatRequest, ChatResponse
from receptionist_service import handle_intent
from timing import measure_ai, start_tracking

router = APIRouter(tags=["Chat"])
logger = logging.getLogger("uvicorn.error")


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, response: Response):
    total_start = time.perf_counter()
    tracker = start_tracking()
    current_date = Date.today().isoformat()

    try:
        with measure_ai():
            intent = interpret_message(request.message, current_date=current_date)
    except AIServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI service unavailable: {e}",
        )

    result = handle_intent(intent)

    total_ms = (time.perf_counter() - total_start) * 1000
    other_ms = total_ms - tracker.ai_ms - tracker.db_ms

    response.headers["X-Latency-Total-Ms"] = f"{total_ms:.1f}"
    response.headers["X-Latency-AI-Ms"] = f"{tracker.ai_ms:.1f}"
    response.headers["X-Latency-DB-Ms"] = f"{tracker.db_ms:.1f}"
    response.headers["X-Latency-Other-Ms"] = f"{other_ms:.1f}"

    logger.info(
        "chat intent=%s total=%.1fms ai=%.1fms db=%.1fms (%d calls) other=%.1fms",
        intent.intent, total_ms, tracker.ai_ms, tracker.db_ms,
        tracker.db_calls, other_ms,
    )
    return result