import logging
from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from app.api.v1.schemas import ChatRequest, ChatResponse
from app.services.rag_service import rag_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    return rag_service.answer_question(request)


@router.post("/stream")
async def chat_stream(request: ChatRequest) -> EventSourceResponse:
    async def event_generator():
        try:
            async for event in rag_service.answer_question_stream(request):
                yield event
        except Exception as e:
            logger.error(f"Error in chat stream: {e}", exc_info=True)
            yield {"event": "error", "data": f"Error: {str(e)}"}
    
    return EventSourceResponse(event_generator())
