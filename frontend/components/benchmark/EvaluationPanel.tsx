"use client";

import { EmbeddingModelMetric, ChartPoint, EvaluateResponse } from "@/lib/api";

interface EvaluationPanelProps {
  models: EmbeddingModelMetric[];
  heatmap: ChartPoint[];
  onEvaluate: () => void;
  isEvaluating?: boolean;
  evalResult?: EvaluateResponse | null;
}

export function EvaluationPanel({ models, heatmap, onEvaluate, isEvaluating, evalResult }: EvaluationPanelProps) {
  const details = evalResult?.details;

  return (
    <div className="space-y-4 rounded-[16px] border border-[#DDE5DF] bg-white p-4 shadow-sm">
      <div className="flex items-center justify-between gap-3">
        <div>
          <div className="text-sm font-bold text-[#0F2916]">RAGAS Evaluation</div>
          <div className="text-xs text-[#5B7361]">Faithfulness, relevancy, and hallucination analysis.</div>
        </div>
        <button
          onClick={onEvaluate}
          disabled={isEvaluating}
          className="rounded-[10px] bg-[#1B4332] px-4 py-2 text-xs font-bold text-white transition-colors hover:bg-[#2D6A4F] disabled:opacity-60"
        >
          {isEvaluating ? "Evaluating…" : "Run RAGAS Eval"}
        </button>
      </div>

      {/* Real RAGAS results */}
      {details && (
        <div className="rounded-[12px] border border-emerald-200 bg-emerald-50 p-3 space-y-2">
          <div className="text-xs font-bold text-emerald-800 uppercase tracking-widest">Latest Evaluation Result</div>
          <div className="grid grid-cols-2 gap-2">
            {[
              { label: "Faithfulness", value: details.faithfulness as string | null, subtext: details.faithfulness_reason as string | null },
              { label: "Relevancy", value: details.answer_relevancy as string | null, subtext: details.relevancy_reason as string | null },
            ].map(({ label, value, subtext }) => (
              <div key={label} className="rounded-lg border border-emerald-100 bg-white p-2.5">
                <div className="text-xs font-semibold text-slate-500">{label}</div>
                <div className={`mt-1 text-sm font-bold ${
                  value === "faithful" || value === "relevant" ? "text-emerald-700" :
                  value === "unfaithful" || value === "irrelevant" ? "text-red-600" : "text-slate-500"
                }`}>
                  {value ?? "–"}
                </div>
                {subtext && <p className="mt-1 text-[10px] text-slate-500 leading-tight line-clamp-2">{subtext}</p>}
              </div>
            ))}
          </div>
          <div className="text-xs text-emerald-700 font-semibold">
            Blended score: {((evalResult?.experiment.score ?? 0) * 100).toFixed(0)}% · {evalResult?.experiment.experiment_id}
          </div>
        </div>
      )}

      {/* Embedding model comparison */}
      <div>
        <div className="mb-2 text-xs font-bold text-[#0F2916]">Embedding Model Comparison</div>
        <div className="space-y-3">
          {models.map((model) => (
            <div key={model.model} className="rounded-[12px] border border-[#E1E8E3] bg-[#F8FAF8] p-3">
              <div className="flex items-center justify-between text-sm">
                <span className="font-bold text-[#0F2916]">{model.model}</span>
                <span className="text-xs text-[#5B7361]">{model.speed_ms} ms</span>
              </div>
              <div className="mt-3 h-2 overflow-hidden rounded-full bg-[#E1E8E3]">
                <div className="h-full rounded-full bg-[#2D6A4F]" style={{ width: `${model.retrieval_quality * 100}%` }} />
              </div>
              <div className="mt-2 text-xs text-[#5B7361]">{Math.round(model.retrieval_quality * 100)}% quality · {model.memory_mb} MB</div>
            </div>
          ))}
        </div>
      </div>

      {/* Confidence heatmap */}
      <div>
        <div className="mb-3 text-sm font-bold text-[#0F2916]">Confidence Heatmap</div>
        <div className="grid grid-cols-2 gap-2">
          {heatmap.map((item) => (
            <div key={item.label} className="rounded-[10px] px-3 py-3 text-xs font-bold text-[#0F2916]" style={{ backgroundColor: `rgba(45, 106, 79, ${0.12 + item.value * 0.42})` }}>
              <div>{item.label}</div>
              <div className="mt-1 text-[#1B4332]">{Math.round(item.value * 100)}%</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

