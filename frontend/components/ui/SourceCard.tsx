"use client";

import { SourceSpan } from "@/lib/api";

interface SourceCardProps {
  source: SourceSpan;
}

export function SourceCard({ source }: SourceCardProps) {
  return (
    <div className="rounded-[18px] border border-[#E5E7EB] bg-white p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-semibold text-[#111827]">{source.title || "Source document"}</p>
          <p className="mt-1 text-[12px] text-[#6B7280]">Page {source.page ?? "—"} · Score {source.score.toFixed(2)}</p>
        </div>
      </div>
      <p className="mt-3 text-sm leading-6 text-[#4B5563]">{source.text.slice(0, 120)}...</p>
      <div className="mt-3 h-1 rounded-full bg-[#EAF7EF]">
        <div className="h-full rounded-full bg-[#1F6F50]" style={{ width: `${Math.min(source.score * 100, 100)}%` }} />
      </div>
    </div>
  );
}
