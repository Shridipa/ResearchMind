from fastapi import APIRouter

from app.api.v1.schemas import FlashcardRequest, FlashcardResponse
from app.services.study_service import study_service

router = APIRouter()


@router.post("", response_model=FlashcardResponse)
def generate_flashcards(request: FlashcardRequest) -> FlashcardResponse:
    return study_service.generate_flashcards(request)
