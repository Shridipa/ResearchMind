from fastapi import APIRouter, File, HTTPException, UploadFile

from app.api.v1.schemas import (
    PaperActionRequest,
    PaperActionResponse,
    PaperRecord,
    PaperSearchRequest,
    PaperSearchResponse,
    SummaryRequest,
    SummaryResponse,
    UploadResponse,
)
from app.core.errors import EmptyDocumentError
from app.services.paper_service import paper_service

router = APIRouter()


@router.get("", response_model=list[PaperRecord])
def list_papers() -> list[PaperRecord]:
    return paper_service.list_papers()


@router.get("/{paper_id}", response_model=PaperRecord)
def get_paper(paper_id: str) -> PaperRecord:
    paper = paper_service.get_paper(paper_id)
    if paper is None:
        raise HTTPException(status_code=404, detail="Paper not found.")
    return paper


@router.delete("/{paper_id}")
def delete_paper(paper_id: str) -> dict[str, bool]:
    try:
        paper_service.delete_paper(paper_id)
        return {"deleted": True}
    except KeyError:
        raise HTTPException(status_code=404, detail="Paper not found.")


@router.post("/upload", response_model=UploadResponse)
async def upload_paper(file: UploadFile = File(...)) -> UploadResponse:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF uploads are supported.")
    try:
        return await paper_service.ingest_upload(file)
    except EmptyDocumentError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/summarize", response_model=SummaryResponse)
def summarize_paper(request: SummaryRequest) -> SummaryResponse:
    return paper_service.summarize(request.paper_id)


@router.post("/search", response_model=PaperSearchResponse)
def search_papers(request: PaperSearchRequest) -> PaperSearchResponse:
    return PaperSearchResponse(
        query=request.query,
        results=paper_service.search_papers(request.query, request.top_k),
    )


@router.post("/actions/{action}", response_model=PaperActionResponse)
def run_paper_action(action: str, request: PaperActionRequest) -> PaperActionResponse:
    return paper_service.action(action, request.paper_id)
