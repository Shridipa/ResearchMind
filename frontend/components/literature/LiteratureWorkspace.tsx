"use client";

import { useState } from "react";
import { BookOpen, Sparkles, AlertCircle, ChevronDown, ChevronUp, ExternalLink } from "lucide-react";
import { generateLiteratureReview, LiteratureReviewResponse, SourceSpan } from "@/lib/api";

function SourceCard({ source }: { source: SourceSpan }) {
  const [expanded, setExpanded] = useState(false);
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-3">
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <p className="truncate text-sm font-semibold text-slate-800">{source.title ?? "Unknown paper"}</p>
          <p className="mt-0.5 text-xs text-slate-400">Page {source.page} · Score {(source.score * 100).toFixed(0)}%</p>
        </div>
        <button
          onClick={() => setExpanded((v) => !v)}
          className="shrink-0 text-slate-400 hover:text-slate-600"
          title={expanded ? "Collapse" : "Expand"}
        >
          {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        </button>
      </div>
      {expanded && (
        <p className="mt-2 text-xs leading-relaxed text-slate-600 border-t border-slate-100 pt-2">
          {source.text.slice(0, 400)}{source.text.length > 400 ? "…" : ""}
        </p>
      )}
    </div>
  );
}

function ReviewOutput({ result }: { result: LiteratureReviewResponse }) {
  const confidencePct = Math.round(result.confidence * 100);
  const riskPct = Math.round(result.unsupported_claim_risk * 100);

  return (
    <div className="flex gap-6 h-full overflow-hidden">
      {/* Main review */}
      <div className="flex-1 overflow-y-auto">
        {/* Stats bar */}
        <div className="mb-5 flex flex-wrap gap-3">
          <div className="rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">
            Confidence {confidencePct}%
          </div>
          <div className={`rounded-full border px-3 py-1 text-xs font-semibold ${
            riskPct < 30 ? "border-emerald-200 bg-emerald-50 text-emerald-700" :
            riskPct < 60 ? "border-amber-200 bg-amber-50 text-amber-700" :
            "border-red-200 bg-red-50 text-red-700"
          }`}>
            Hallucination risk {riskPct}%
          </div>
          <div className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-semibold text-slate-600">
            {result.sources.length} sources cited
          </div>
        </div>

        {/* Markdown-style review rendered as plain text with section headers */}
        <div className="prose prose-sm max-w-none">
          {result.review.split("\n").map((line, i) => {
            if (line.startsWith("## ")) return <h2 key={i} className="mt-6 mb-2 text-base font-bold text-slate-900 border-b border-slate-100 pb-1">{line.slice(3)}</h2>;
            if (line.startsWith("### ")) return <h3 key={i} className="mt-4 mb-1.5 text-sm font-semibold text-slate-800">{line.slice(4)}</h3>;
            if (line.startsWith("**") && line.endsWith("**")) return <p key={i} className="mt-3 font-semibold text-slate-800">{line.slice(2, -2)}</p>;
            if (line.startsWith("- ")) return <li key={i} className="ml-4 text-sm text-slate-700 list-disc">{line.slice(2)}</li>;
            if (line.trim() === "") return <div key={i} className="h-2" />;
            return <p key={i} className="text-sm leading-relaxed text-slate-700">{line}</p>;
          })}
        </div>
      </div>

      {/* Sources sidebar */}
      <div className="w-72 shrink-0 overflow-y-auto">
        <h3 className="mb-3 text-xs font-bold uppercase tracking-widest text-slate-400">Evidence Sources</h3>
        <div className="space-y-2">
          {result.sources.map((s) => (
            <SourceCard key={s.chunk_id} source={s} />
          ))}
        </div>
      </div>
    </div>
  );
}

export function LiteratureWorkspace() {
  const [topic, setTopic] = useState("");
  const [result, setResult] = useState<LiteratureReviewResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (!topic.trim() || isLoading) return;
    setIsLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await generateLiteratureReview(topic.trim());
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to generate review.");
    } finally {
      setIsLoading(false);
    }
  };

  const EXAMPLE_TOPICS = [
    "Transformer models in NLP",
    "Attention mechanisms in deep learning",
    "RAG systems for knowledge retrieval",
    "Left-digit bias in financial markets",
  ];

  return (
    <div className="flex h-full flex-col bg-white p-6">
      {/* Header */}
      <div className="mb-6 flex items-center gap-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-emerald-100">
          <BookOpen size={18} className="text-emerald-700" />
        </div>
        <div>
          <h1 className="text-lg font-bold text-slate-900">Literature Review Generator</h1>
          <p className="text-sm text-slate-500">Generate multi-paper synthesis grounded in your indexed corpus</p>
        </div>
      </div>

      {/* Input */}
      <div className="mb-4 flex gap-3">
        <input
          type="text"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleGenerate()}
          placeholder="e.g. Transformer models in NLP, RAG systems…"
          className="flex-1 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-emerald-400 focus:bg-white focus:ring-2 focus:ring-emerald-100"
        />
        <button
          onClick={handleGenerate}
          disabled={isLoading || !topic.trim()}
          className="flex items-center gap-2 rounded-xl bg-emerald-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:opacity-50"
        >
          <Sparkles size={15} />
          {isLoading ? "Generating…" : "Generate"}
        </button>
      </div>

      {/* Example topics */}
      {!result && !isLoading && (
        <div className="mb-6 flex flex-wrap gap-2">
          {EXAMPLE_TOPICS.map((t) => (
            <button
              key={t}
              onClick={() => setTopic(t)}
              className="rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-600 transition hover:border-emerald-300 hover:bg-emerald-50 hover:text-emerald-700"
            >
              {t}
            </button>
          ))}
        </div>
      )}

      {/* States */}
      {error && (
        <div className="mb-4 flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          <AlertCircle size={15} className="shrink-0" />
          {error}
        </div>
      )}

      {isLoading && (
        <div className="flex flex-1 flex-col items-center justify-center gap-4 text-center">
          <div className="relative flex h-16 w-16 items-center justify-center">
            <div className="absolute inset-0 animate-spin rounded-full border-4 border-emerald-100 border-t-emerald-500" />
            <BookOpen size={22} className="text-emerald-600" />
          </div>
          <div>
            <p className="font-semibold text-slate-800">Synthesizing literature review…</p>
            <p className="mt-1 text-sm text-slate-500">Retrieving evidence across papers · Grounding claims · Generating synthesis</p>
          </div>
        </div>
      )}

      {result && !isLoading && (
        <div className="flex-1 overflow-hidden">
          <ReviewOutput result={result} />
        </div>
      )}

      {!result && !isLoading && !error && (
        <div className="flex flex-1 flex-col items-center justify-center gap-3 text-center text-slate-400">
          <div className="rounded-full bg-slate-100 p-4">
            <BookOpen size={28} className="text-slate-300" />
          </div>
          <p className="text-sm">Enter a research topic above to generate a grounded literature review from your indexed papers.</p>
        </div>
      )}
    </div>
  );
}
