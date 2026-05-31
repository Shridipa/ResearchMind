"use client";

import { SourceSpan } from "@/lib/api";
import { BookOpen, ShieldCheck } from "lucide-react";

interface CitationCardProps {
  source: SourceSpan;
}

export function CitationCard({ source }: CitationCardProps) {
  return (
    <div className="py-2">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-medium text-[#111827]">{source.title || source.paper_id || "Source document"}</p>
          <p className="mt-1 text-xs text-[#6B7280]">Page {source.page ?? "—"} · Score {source.score.toFixed(3)}</p>
        </div>
        <div className="inline-flex items-center gap-2 px-2 py-1 text-[11px] font-semibold text-[#1F6F50]">
          <ShieldCheck size={14} /> Verified
        </div>
      </div>
      <p className="mt-2 text-sm leading-6 text-[#374151]">{source.text}</p>
    </div>
  );
}
