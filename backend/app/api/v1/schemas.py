from pydantic import BaseModel, Field


class RetrievalStats(BaseModel):
    semantic_score: float | None = None
    bm25_score: float | None = None
    final_score: float
    retrieval_mode: str


class SummarizationStats(BaseModel):
    mode: str  # "extractive", "transformer", "llm"
    tokens_saved: int = 0
    api_calls_avoided: int = 0
    cache_hit: bool = False


class GroundingStats(BaseModel):
    groundedness_score: float  # 0-100
    hallucination_risk: float  # 0-100
    risk_level: str  # low, medium, high
    supported_claims: int
    total_claims: int


class SourceSpan(BaseModel):
    paper_id: str
    title: str | None = None
    page: int | None = None
    chunk_id: str
    score: float
    text: str


class UploadResponse(BaseModel):
    paper_id: str
    filename: str
    chunks_indexed: int
    citations_found: int


class PaperRecord(BaseModel):
    paper_id: str
    filename: str
    title: str
    chunks_indexed: int
    citations_found: int
    file_path: str = ""
    status: str = "indexed"
    processing_state: str = "ready"
    embedding_status: str = "indexed"
    upload_date: str
    authors: list[str] = Field(default_factory=list)
    abstract: str | None = None
    sections: list[str] = Field(default_factory=list)
    methodology: str | None = None
    limitations: list[str] = Field(default_factory=list)
    key_contributions: list[str] = Field(default_factory=list)
    citations: list[str] = Field(default_factory=list)
    summary: dict[str, str | list[str]] | None = None


class PaperSearchRequest(BaseModel):
    query: str = Field(min_length=2)
    top_k: int = Field(default=5, ge=1, le=20)


class PaperSearchResult(PaperRecord):
    similarity_score: float


class PaperSearchResponse(BaseModel):
    query: str
    results: list[PaperSearchResult]


class PaperActionRequest(BaseModel):
    paper_id: str | None = None
    paper_ids: list[str] | None = None
    query: str | None = None


class PaperActionResponse(BaseModel):
    action: str
    status: str
    result: dict[str, str | list[str] | list[dict[str, str]]]


class ChatRequest(BaseModel):
    question: str = Field(min_length=3)
    session_id: str | None = None
    paper_ids: list[str] | None = None
    top_k: int = 5
    retrieval_mode: str = Field(default="hybrid", description="hybrid, semantic, or bm25")


class ProviderMetadata(BaseModel):
    selected_model: str
    latency_ms: float
    retry_count: int
    fallback_triggered: bool
    attempted_models: list[str]
    error: str | None = None


class ChatResponse(BaseModel):
    answer: str
    confidence: float
    sources: list[SourceSpan]
    unsupported_claim_risk: float
    provider_metadata: ProviderMetadata | None = None
    retrieval_stats: RetrievalStats | None = None
    grounding_stats: GroundingStats | None = None


class SummaryRequest(BaseModel):
    paper_id: str


class SummaryResponse(BaseModel):
    paper_id: str
    summary: dict[str, str | list[str]]
    sources: list[SourceSpan]
    summarization_stats: SummarizationStats | None = None


class SectionComparison(BaseModel):
    section_name: str
    similarity_score: float
    key_differences: list[str]
    key_similarities: list[str]
    paper1_length: int
    paper2_length: int


class PaperComparisonResponse(BaseModel):
    paper1_id: str
    paper1_title: str
    paper2_id: str
    paper2_title: str
    overall_similarity: float
    shared_concepts: list[str]
    distinctive_concepts_p1: list[str]
    distinctive_concepts_p2: list[str]
    relationship_type: str  # building_on, alternative, complementary, unrelated
    confidence: float
    section_comparisons: dict[str, SectionComparison]
    recommendations: list[str]


class ComparisonRequest(BaseModel):
    paper1_id: str
    paper2_id: str


class SessionMetadata(BaseModel):
    session_id: str
    title: str
    created_at: str
    turns_count: int
    papers_used: list[str]
    concepts: list[str]


class TopicGraphSummary(BaseModel):
    total_concepts: int
    total_edges: int
    average_degree: float
    central_concepts: list[str]
    num_clusters: int


class SessionInsights(BaseModel):
    session_summary: str
    total_turns: int
    papers_explored: int
    unique_concepts: int
    average_grounding: float = 0.0
    topic_clusters: int = 0
    divergence_points: int = 0


class SessionResponse(BaseModel):
    session_id: str
    metadata: SessionMetadata
    insights: SessionInsights
    available_context: str
    follow_up_suggestions: list[str]


class MetricPoint(BaseModel):
    name: str
    value: float
    unit: str = ""
    delta: float | None = None
    trend: str = "stable"


class ChartPoint(BaseModel):
    label: str
    value: float
    secondary: float | None = None


class EmbeddingModelMetric(BaseModel):
    model: str
    speed_ms: float
    retrieval_quality: float
    memory_mb: float


class ExperimentRecord(BaseModel):
    experiment_id: str
    dataset: str
    model: str
    metric: str
    score: float
    timestamp: str
    status: str = "completed"


class BenchmarkResponse(BaseModel):
    metrics: list[MetricPoint]
    latency_trends: list[ChartPoint]
    embedding_models: list[EmbeddingModelMetric]
    chunking_strategies: list[ChartPoint]
    hallucination_reduction: list[ChartPoint]
    confidence_heatmap: list[ChartPoint]


class ExperimentsResponse(BaseModel):
    experiments: list[ExperimentRecord]


class EvaluateRequest(BaseModel):
    dataset: str = "sample_qa"
    model: str = "all-MiniLM"
    question: str | None = None
    answer: str | None = None
    contexts: list[str] | None = None


class EvaluateResponse(BaseModel):
    experiment: ExperimentRecord
    details: dict[str, str | float | None] | None = None


class LiteratureReviewRequest(BaseModel):
    topic: str = Field(min_length=3)
    paper_ids: list[str] | None = None


class LiteratureReviewResponse(BaseModel):
    topic: str
    review: str
    confidence: float
    unsupported_claim_risk: float
    sources: list[SourceSpan]


class FlashcardRequest(BaseModel):
    topic: str
    count: int = Field(default=8, ge=1, le=30)
    paper_ids: list[str] | None = None


class Flashcard(BaseModel):
    question: str
    answer: str
    source_chunk_id: str


class FlashcardResponse(BaseModel):
    cards: list[Flashcard]


class CompareRequest(BaseModel):
    paper_ids: list[str] = Field(min_length=2)


class CompareResponse(BaseModel):
    comparison: dict[str, str]
    sources: list[SourceSpan]
