from fastapi import APIRouter

from app.api.v1.schemas import CompareRequest, CompareResponse
from app.services.paper_service import paper_service

router = APIRouter()


@router.post("", response_model=CompareResponse)
def compare_papers(request: CompareRequest) -> CompareResponse:
    return paper_service.compare(request.paper_ids)
