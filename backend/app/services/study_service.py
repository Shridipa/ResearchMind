from app.api.v1.schemas import Flashcard, FlashcardRequest, FlashcardResponse
from app.services.dependencies import get_retriever


class StudyService:
    def generate_flashcards(self, request: FlashcardRequest) -> FlashcardResponse:
        evidence = get_retriever().retrieve(request.topic, request.count, request.paper_ids)
        cards = [
            Flashcard(
                question=f"What is the key idea in source {chunk.chunk_id}?",
                answer=chunk.text[:360],
                source_chunk_id=chunk.chunk_id,
            )
            for chunk, _ in evidence
        ]
        return FlashcardResponse(cards=cards)


study_service = StudyService()
