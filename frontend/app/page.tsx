import Link from "next/link";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "ResearchMind AI — Grounded AI Research Workspace",
  description:
    "Upload academic papers, build semantic indexes, retrieve evidence-backed answers, compare research, and evaluate retrieval quality. A local-first research intelligence platform.",
};

const FEATURES = [
  { name: "Hybrid Retrieval", desc: "Dense semantic search combined with sparse BM25 for maximum recall." },
  { name: "Citation Grounding", desc: "Every answer is anchored to specific page-level evidence from your papers." },
  { name: "Local-First RAG", desc: "High-confidence queries are answered locally without any API call." },
  { name: "Multi-Paper Analysis", desc: "Cross-document semantic comparison powered by paper comparator engine." },
  { name: "Research Memory", desc: "Sessions persist conversation history with grounding scores across turns." },
  { name: "Evaluation Dashboard", desc: "RAGAS-powered faithfulness and relevancy scoring for every run." },
  { name: "Benchmarking", desc: "Live hallucination rate, latency trends, and embedding model comparisons." },
  { name: "Literature Review", desc: "Generate structured literature reviews grounded in your uploaded corpus." },
];

const HOW_IT_WORKS = [
  {
    step: "01",
    title: "Upload Papers",
    points: [
      "PDF ingestion via PyMuPDF",
      "Adaptive chunking with overlap",
      "Metadata extraction (abstract, methodology, limitations)",
      "FAISS vector indexing + BM25 sparse index",
    ],
  },
  {
    step: "02",
    title: "Research Intelligence",
    points: [
      "Hybrid dense + sparse retrieval",
      "Cross-encoder re-ranking",
      "Citation-aware grounded answers",
      "Hallucination detection via evidence matcher",
    ],
  },
  {
    step: "03",
    title: "Evaluation & Benchmarking",
    points: [
      "RAGAS faithfulness + relevancy scoring",
      "Real-time confidence heatmaps",
      "Experiment history persisted locally",
      "Embedding model comparison dashboard",
    ],
  },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white text-slate-900 font-sans">
      {/* ── Navbar ── */}
      <header className="sticky top-0 z-50 border-b border-slate-100 bg-white/95 backdrop-blur-sm">
        <div className="mx-auto flex h-14 max-w-5xl items-center justify-between px-6">
          <div className="flex items-center gap-2.5">
            <div className="flex h-7 w-7 items-center justify-center rounded-md bg-emerald-100">
              <svg viewBox="0 0 16 16" className="h-4 w-4 fill-emerald-700">
                <path d="M8 1a7 7 0 1 0 0 14A7 7 0 0 0 8 1zm0 1.5a5.5 5.5 0 1 1 0 11 5.5 5.5 0 0 1 0-11zM7.25 5v3.25H4v1.5h3.25V13h1.5V9.75H12v-1.5H8.75V5h-1.5z" />
              </svg>
            </div>
            <span className="text-sm font-semibold text-slate-900">ResearchMind AI</span>
          </div>
          <nav className="flex items-center gap-2">
            <Link
              href="/dashboard"
              className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-emerald-700"
            >
              Open Dashboard
            </Link>
          </nav>
        </div>
      </header>

      {/* ── Hero ── */}
      <section className="mx-auto max-w-5xl px-6 pb-16 pt-20 text-center">
        <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700">
          Local-first · Evidence-grounded · Research-grade
        </div>
        <h1 className="mx-auto max-w-3xl text-4xl font-bold leading-[1.15] tracking-tight text-slate-900">
          Grounded AI Research Workspace
        </h1>
        <p className="mx-auto mt-5 max-w-xl text-base leading-relaxed text-slate-500">
          Upload papers, build semantic indexes, retrieve evidence-backed answers, compare research, and evaluate
          retrieval quality — all running locally first.
        </p>

        <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
          <Link
            href="/dashboard"
            className="rounded-lg bg-emerald-600 px-6 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-emerald-700"
          >
            Open Research Workspace →
          </Link>
        </div>

        {/* Workflow trail */}
        <div className="mt-10 flex flex-wrap items-center justify-center gap-2 text-xs text-slate-400">
          {["Upload", "Index", "Retrieve", "Analyze", "Evaluate"].map((step, i, arr) => (
            <span key={step} className="flex items-center gap-2">
              <span className="font-medium text-slate-500">{step}</span>
              {i < arr.length - 1 && <span className="text-slate-300">→</span>}
            </span>
          ))}
        </div>
      </section>

      {/* ── How It Works ── */}
      <section className="border-y border-slate-100 bg-slate-50/60 py-16">
        <div className="mx-auto max-w-5xl px-6">
          <h2 className="mb-10 text-center text-sm font-bold uppercase tracking-widest text-slate-400">
            How It Works
          </h2>
          <div className="grid gap-6 md:grid-cols-3">
            {HOW_IT_WORKS.map((col) => (
              <div
                key={col.step}
                className="rounded-xl border border-slate-200 bg-white p-6"
              >
                <div className="mb-3 text-xs font-bold text-emerald-600">{col.step}</div>
                <h3 className="mb-4 text-base font-semibold text-slate-900">{col.title}</h3>
                <ul className="space-y-2">
                  {col.points.map((point) => (
                    <li key={point} className="flex items-start gap-2 text-sm text-slate-500">
                      <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-emerald-400" />
                      {point}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Features ── */}
      <section className="mx-auto max-w-5xl px-6 py-16">
        <h2 className="mb-10 text-center text-sm font-bold uppercase tracking-widest text-slate-400">
          Platform Features
        </h2>
        <div className="grid gap-x-12 gap-y-6 sm:grid-cols-2">
          {FEATURES.map((feat) => (
            <div key={feat.name} className="flex items-start gap-3 border-b border-slate-100 pb-6">
              <span className="mt-0.5 h-2 w-2 shrink-0 rounded-full bg-emerald-500" />
              <div>
                <div className="text-sm font-semibold text-slate-800">{feat.name}</div>
                <div className="mt-0.5 text-sm text-slate-500">{feat.desc}</div>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-14 rounded-xl border border-emerald-100 bg-emerald-50 p-8 text-center">
          <h3 className="text-lg font-semibold text-emerald-900">
            Ready to start your research session?
          </h3>
          <p className="mt-2 text-sm text-emerald-700">
            Upload your first paper and query it with full citation grounding in under a minute.
          </p>
          <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
            <Link
              href="/dashboard"
              className="rounded-lg bg-emerald-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-emerald-700"
            >
              Open Dashboard →
            </Link>
          </div>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="border-t border-slate-100 py-6 text-center text-xs text-slate-400">
        ResearchMind AI — Local-first research intelligence platform
      </footer>
    </div>
  );
}
