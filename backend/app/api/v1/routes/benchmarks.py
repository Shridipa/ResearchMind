from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter

from app.api.v1.schemas import (
    BenchmarkResponse,
    ChartPoint,
    EmbeddingModelMetric,
    EvaluateRequest,
    EvaluateResponse,
    ExperimentRecord,
    ExperimentsResponse,
    MetricPoint,
)
from app.core.config import settings
import json

EXPERIMENTS_FILE = settings.data_dir / "experiments.json"

def _load_experiments() -> list[ExperimentRecord]:
    if not EXPERIMENTS_FILE.exists():
        return []
    try:
        with EXPERIMENTS_FILE.open("r") as f:
            data = json.load(f)
            return [ExperimentRecord(**d) for d in data]
    except Exception:
        return []

def _save_experiment(exp: ExperimentRecord):
    exps = _load_experiments()
    exps.insert(0, exp)
    EXPERIMENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with EXPERIMENTS_FILE.open("w") as f:
        json.dump([e.model_dump() for e in exps], f, indent=2)

router = APIRouter()



@router.get("", response_model=BenchmarkResponse)
def get_benchmarks() -> BenchmarkResponse:
    return BenchmarkResponse(
        metrics=[
            MetricPoint(name="Retrieval accuracy", value=87.4, unit="%", delta=5.2, trend="up"),
            MetricPoint(name="Semantic similarity", value=0.82, delta=0.04, trend="up"),
            MetricPoint(name="Hallucination rate", value=6.8, unit="%", delta=-3.1, trend="down"),
            MetricPoint(name="Response latency", value=142, unit="ms", delta=-18, trend="down"),
            MetricPoint(name="Chunk precision", value=79.5, unit="%", delta=4.4, trend="up"),
            MetricPoint(name="Token efficiency", value=71.2, unit="%", delta=2.7, trend="up"),
        ],
        latency_trends=[
            ChartPoint(label="Mon", value=196),
            ChartPoint(label="Tue", value=172),
            ChartPoint(label="Wed", value=151),
            ChartPoint(label="Thu", value=146),
            ChartPoint(label="Fri", value=142),
        ],
        embedding_models=[
            EmbeddingModelMetric(model="all-MiniLM", speed_ms=72, retrieval_quality=0.76, memory_mb=88),
            EmbeddingModelMetric(model="BGE embeddings", speed_ms=118, retrieval_quality=0.87, memory_mb=214),
            EmbeddingModelMetric(model="E5 embeddings", speed_ms=135, retrieval_quality=0.84, memory_mb=248),
        ],
        chunking_strategies=[
            ChartPoint(label="Fixed 512", value=0.71, secondary=96),
            ChartPoint(label="Adaptive 900", value=0.82, secondary=142),
            ChartPoint(label="Section-aware", value=0.86, secondary=168),
        ],
        hallucination_reduction=[
            ChartPoint(label="No cites", value=18.4),
            ChartPoint(label="Top-k cites", value=10.7),
            ChartPoint(label="Confidence gate", value=6.8),
        ],
        confidence_heatmap=[
            ChartPoint(label="Abstract", value=0.91),
            ChartPoint(label="Methods", value=0.84),
            ChartPoint(label="Results", value=0.79),
            ChartPoint(label="Limitations", value=0.68),
        ],
    )


@router.get("/experiments", response_model=ExperimentsResponse)
def get_experiments() -> ExperimentsResponse:
    return ExperimentsResponse(experiments=_load_experiments())


@router.post("/evaluate", response_model=EvaluateResponse)
async def evaluate(request: EvaluateRequest) -> EvaluateResponse:
    """Run a real RAGAS-powered evaluation on a question/answer/context triple."""
    from app.evaluation.ragas_evaluator import ragas_evaluator

    eval_results = await ragas_evaluator.evaluate_rag_pipeline(
        question=request.question or "",
        response=request.answer or "",
        contexts=request.contexts or [],
    )

    # Compute a blended numeric score from faithfulness + relevancy
    score_map = {"faithful": 1.0, "unfaithful": 0.0, "relevant": 1.0, "irrelevant": 0.0}
    f_score = score_map.get(eval_results.get("faithfulness") or "", 0.5)
    r_score = score_map.get(eval_results.get("answer_relevancy") or "", 0.5)
    blended = round((f_score + r_score) / 2, 4)

    exp = ExperimentRecord(
        experiment_id=f"EXP-{uuid4().hex[:6].upper()}",
        dataset=request.dataset,
        model=request.model,
        metric="faithfulness+relevancy",
        score=blended,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
    _save_experiment(exp)

    return EvaluateResponse(
        experiment=exp,
        details=eval_results,
    )

