"use client";

import { useEffect, useState } from "react";
import { listPapers, PaperRecord, SourceSpan, ChatResponse } from "@/lib/api";
import { CitationCard } from "./CitationCard";
import { Layers, BookOpen, BarChart3, Settings2 } from "lucide-react";

const CONTEXT_TABS = [
  { label: "Sources", icon: Layers },
  { label: "Papers", icon: BookOpen },
  { label: "Benchmarks", icon: BarChart3 },
  { label: "Settings", icon: Settings2 },
];

interface ContextPanelProps {
  answer: ChatResponse | null;
  isStreaming: boolean;
  refreshKey: number;
}

export function ContextPanel({ answer, isStreaming, refreshKey }: ContextPanelProps) {
  const [activeTab, setActiveTab] = useState("Sources");
  const [papers, setPapers] = useState<PaperRecord[]>([]);
  const [loadingPapers, setLoadingPapers] = useState(false);
  const sources = answer?.sources ?? [];

  useEffect(() => {
    if (activeTab !== "Papers") return;

    let canceled = false;
    setLoadingPapers(true);

    listPapers()
      .then((results) => {
        if (!canceled) {
          setPapers(results.slice(0, 5));
        }
      })
      .catch(() => {
        if (!canceled) setPapers([]);
      })
      .finally(() => {
        if (!canceled) setLoadingPapers(false);
      });

    return () => {
      canceled = true;
    };
  }, [activeTab, refreshKey]);

  return (
    <aside className="flex min-h-[720px] w-full flex-col rounded-[28px] border border-slate-200 bg-white px-4 py-4 shadow-sm">
      <div className="mb-4 flex items-center justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Context</p>
          <h2 className="mt-1 text-sm font-semibold text-slate-900">Research assistant</h2>
        </div>
        <div className="text-xs text-slate-500">{answer ? (isStreaming ? "Streaming" : "Ready") : "Waiting"}</div>
      </div>

      <div className="mb-4 flex flex-wrap gap-2">
        {CONTEXT_TABS.map((tab) => {
          const Icon = tab.icon;
          const active = tab.label === activeTab;
          return (
            <button
              key={tab.label}
              onClick={() => setActiveTab(tab.label)}
              className={`inline-flex items-center gap-2 rounded-full px-3 py-2 text-sm font-medium transition ${
                active ? "bg-emerald-50 text-emerald-800" : "text-slate-600 hover:bg-slate-100"
              }`}
            >
              <Icon size={14} />
              {tab.label}
            </button>
          );
        })}
      </div>

      <div className="space-y-4 overflow-y-auto pb-4">
        {activeTab === "Sources" && (
          <div className="space-y-4">
            {sources.length ? (
              sources.slice(0, 4).map((source: SourceSpan) => <CitationCard key={source.chunk_id} source={source} />)
            ) : (
              <div className="rounded-[24px] border border-dashed border-slate-200 bg-slate-50 p-6 text-sm text-slate-600">
                Sources appear here after a grounded response.
              </div>
            )}
          </div>
        )}

        {activeTab === "Papers" && (
          <div className="space-y-3">
            <div>
              <p className="text-sm font-semibold text-slate-900">Uploaded papers</p>
              <p className="mt-1 text-xs text-slate-500">Freshly indexed documents appear here after upload.</p>
            </div>

            {loadingPapers ? (
              <div className="rounded-[24px] bg-slate-50 p-6 text-sm text-slate-600">Loading papers…</div>
            ) : papers.length ? (
              <div className="space-y-3">
                {papers.map((paper) => (
                  <div key={paper.paper_id} className="rounded-[22px] border border-slate-100 bg-slate-50 p-4">
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <p className="font-semibold text-slate-900">{paper.title || paper.filename}</p>
                        <p className="mt-1 text-xs uppercase tracking-[0.18em] text-slate-500">{paper.upload_date}</p>
                      </div>
                      <span className="rounded-full bg-emerald-100 px-3 py-1 text-[11px] font-semibold text-emerald-700">{paper.processing_state}</span>
                    </div>
                    <div className="mt-3 flex flex-wrap gap-2 text-xs text-slate-600">
                      <span>{paper.chunks_indexed} chunks</span>
                      <span>{paper.citations_found} citations</span>
                      <span>{paper.embedding_status}</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="rounded-[24px] border border-dashed border-slate-200 bg-slate-50 p-6 text-sm text-slate-600">
                No papers have been indexed yet. Upload a document to start the research workflow.
              </div>
            )}
          </div>
        )}

        {activeTab === "Benchmarks" && (
          <div className="space-y-3">
            <p className="text-sm font-semibold text-slate-900">Retrieval metrics</p>
            <div className="space-y-2 text-sm text-slate-600">
              <div className="flex items-center justify-between rounded-2xl bg-slate-50 px-4 py-3">
                <span>Precision</span>
                <span className="font-semibold text-emerald-700">93%</span>
              </div>
              <div className="flex items-center justify-between rounded-2xl bg-slate-50 px-4 py-3">
                <span>Hallucination risk</span>
                <span className="font-semibold text-emerald-700">7%</span>
              </div>
              <div className="flex items-center justify-between rounded-2xl bg-slate-50 px-4 py-3">
                <span>Latency</span>
                <span className="font-semibold text-emerald-700">320ms</span>
              </div>
            </div>
          </div>
        )}

        {activeTab === "Settings" && (
          <div className="space-y-3">
            <div>
              <p className="text-sm font-semibold text-slate-900">Active model</p>
              <p className="mt-1 text-sm font-semibold text-emerald-700">OpenRouter</p>
              <p className="mt-1 text-xs text-slate-500">OpenRouter provider · streaming enabled</p>
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-900">Retrieval settings</p>
              <p className="mt-1 text-xs text-slate-500">top_k 5 · chunk size 900 · rerank depth 5</p>
            </div>
          </div>
        )}
      </div>
    </aside>
  );
}
