"use client";

import { motion } from "framer-motion";
import { PaperRecord } from "@/lib/api";
import { Zap, Cpu, Cloud } from "lucide-react";
import { ActionToolbar } from "../ActionToolbar";

interface PaperDetailPanelProps {
  paper: PaperRecord | null;
  runningAction?: string;
  actionResult?: string;
  isDeleting?: boolean;
  onAction: (action: string) => void;
  onDelete?: (paperId: string) => void;
  summarizationStats?: any;
}

function ListBlock({ title, items }: { title: string; items: string[] }) {
  return (
    <div>
      <div className="mb-2 text-[11px] font-bold uppercase tracking-[0.12em] text-[#5B7361]">{title}</div>
      <div className="space-y-2">
        {items.length ? (
          items.map((item) => (
            <div key={item} className="rounded-[10px] border border-[#E1E8E3] bg-[#F8FAF8] px-3 py-2 text-xs text-[#1B3B22]">
              {item}
            </div>
          ))
        ) : (
          <div className="text-xs text-[#829987]">Run an AI action to populate this section.</div>
        )}
      </div>
    </div>
  );
}

type SummaryMode = "extractive" | "transformer" | "llm";

function isSummaryMode(mode: string): mode is SummaryMode {
  return mode === "extractive" || mode === "transformer" || mode === "llm";
}

function SummarizationBadge({ mode }: { mode: string }) {
  const normalizedMode: SummaryMode = isSummaryMode(mode) ? mode : "extractive";
  const icons = {
    extractive: <Cpu size={12} />,
    transformer: <Zap size={12} />,
    llm: <Cloud size={12} />,
  };
  
  const colors = {
    extractive: "bg-[#E0F2FE] text-[#0369A1]",
    transformer: "bg-[#FBBF24]/10 text-[#B45309]",
    llm: "bg-[#DDD6FE] text-[#7C3AED]",
  };
  
  return (
    <span className={`inline-flex items-center gap-1 rounded-full px-2 py-1 text-[10px] font-semibold ${colors[normalizedMode]}`}>
      {icons[normalizedMode]}
      {normalizedMode === "extractive" && "Local Extractive"}
      {normalizedMode === "transformer" && "Neural Summarization"}
      {normalizedMode === "llm" && "LLM Generated"}
    </span>
  );
}

export function PaperDetailPanel({ paper, runningAction, actionResult, isDeleting, onAction, onDelete, summarizationStats }: PaperDetailPanelProps) {
  if (!paper) {
    return (
      <div className="flex min-h-[520px] items-center justify-center rounded-[18px] border border-dashed border-[#CFE0D5] bg-white text-sm text-[#5B7361]">
        Select a paper to inspect its research profile.
      </div>
    );
  }

  const summaryItems = paper.summary
    ? Object.entries(paper.summary).map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join("; ") : value}`)
    : [];

  return (
    <motion.aside
      key={paper.paper_id}
      initial={{ opacity: 0, x: 16 }}
      animate={{ opacity: 1, x: 0 }}
      className="rounded-[18px] border border-[#DDE5DF] bg-white p-5 shadow-sm"
    >
      <div className="mb-5 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <div className="text-[11px] font-bold uppercase tracking-[0.16em] text-[#2D6A4F]">Paper Detail</div>
          <h2 className="mt-2 text-xl font-bold text-[#0F2916]">{paper.title}</h2>
          <p className="mt-2 text-sm text-[#5B7361]">{paper.filename}</p>
          <div className="mt-3 flex flex-wrap items-center gap-2 text-xs text-[#334E3A]">
            <span className="rounded-full bg-[#EAF5EF] px-2 py-1">{paper.processing_state}</span>
            <span className="rounded-full bg-[#EDF8FF] px-2 py-1">{paper.embedding_status}</span>
            <span className="rounded-full bg-[#F8FAF8] px-2 py-1">Uploaded {new Date(paper.upload_date).toLocaleDateString()}</span>
          </div>
        </div>

        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => paper.paper_id && onDelete?.(paper.paper_id)}
            disabled={!paper || isDeleting}
            className="inline-flex items-center justify-center rounded-[10px] border border-red-200 bg-red-50 px-4 py-2 text-xs font-bold text-red-700 transition hover:bg-red-100 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isDeleting ? "Deleting..." : "Delete paper"}
          </button>
        </div>
      </div>

      <ActionToolbar disabled={!paper} runningAction={runningAction} onAction={onAction} />

      {actionResult && (
        <div className="mt-4 rounded-[12px] border border-[#CFE0D5] bg-[#EAF5EF] px-4 py-3 text-sm text-[#1B4332]">
          {actionResult}
        </div>
      )}

      <div className="mt-6 space-y-6">
        <div className="space-y-4">
          <div>
            <div className="mb-2 text-[11px] font-bold uppercase tracking-[0.12em] text-[#5B7361]">Abstract</div>
            <p className="rounded-[14px] border border-[#E1E8E3] bg-[#F8FAF8] p-4 text-sm leading-7 text-[#1B3B22]">
              {paper.abstract || "Abstract extraction will appear after document processing."}
            </p>
          </div>

          <div className="grid gap-3 sm:grid-cols-2">
            <div className="rounded-[14px] border border-[#E1E8E3] bg-[#FCFCFC] p-4">
              <div className="mb-2 text-[11px] font-bold uppercase tracking-[0.12em] text-[#5B7361]">Authors</div>
              <p className="text-sm text-[#334E3A]">{paper.authors.length ? paper.authors.join(", ") : "No authors extracted."}</p>
            </div>
            <div className="rounded-[14px] border border-[#E1E8E3] bg-[#FCFCFC] p-4">
              <div className="mb-2 text-[11px] font-bold uppercase tracking-[0.12em] text-[#5B7361]">Chunk coverage</div>
              <p className="text-sm text-[#334E3A]">{paper.chunks_indexed} chunks indexed for search and retrieval.</p>
            </div>
          </div>

          <ListBlock title="Extracted Sections" items={paper.sections} />
          <ListBlock title="Key Contributions" items={paper.key_contributions} />
          <ListBlock title="Methodology" items={paper.methodology ? [paper.methodology] : []} />
          <ListBlock title="Limitations" items={paper.limitations} />
          <ListBlock title="Citations" items={paper.citations} />
        </div>

        <div>
          <div className="mb-2 flex items-center justify-between">
            <span className="text-[11px] font-bold uppercase tracking-[0.12em] text-[#5B7361]">Generated Summary</span>
            {summarizationStats && (
              <SummarizationBadge mode={summarizationStats.mode} />
            )}
          </div>
          {summaryItems.length ? (
            <div className="space-y-2">
              {summaryItems.map((item) => (
                <div key={item} className="rounded-[10px] border border-[#E1E8E3] bg-[#F8FAF8] px-3 py-2 text-xs text-[#1B3B22]">
                  {item}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-xs text-[#829987]">Summary will appear after processing.</div>
          )}
        </div>
      </div>
    </motion.aside>
  );
}
