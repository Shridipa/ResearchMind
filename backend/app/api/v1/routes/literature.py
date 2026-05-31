from fastapi import APIRouter

from app.api.v1.schemas import LiteratureReviewRequest, LiteratureReviewResponse
from app.services.literature_service import literature_service

router = APIRouter()


@router.post("", response_model=LiteratureReviewResponse)
def generate_review(request: LiteratureReviewRequest) -> LiteratureReviewResponse:
    result = literature_service.generate_review(request.topic, request.paper_ids)
    return LiteratureReviewResponse(**result)

