"use client";

import { useEffect, useState } from "react";
import { listPapers, PaperRecord } from "@/lib/api";

export function PapersPanel() {
  const [papers, setPapers] = useState<PaperRecord[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const next = await listPapers();
        setPapers(next.slice(0, 4));
      } catch {
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <div className="space-y-3">
      <div className="rounded-[18px] border border-[#E5E7EB] bg-white p-4 text-sm text-[#111827]">
        <div className="text-xs uppercase tracking-[0.2em] text-[#6B7280]">Papers</div>
        <div className="mt-2 text-sm text-[#374151]">Recent uploaded and indexed documents.</div>
      </div>
      <div className="space-y-3 overflow-hidden rounded-[18px] border border-[#E5E7EB] bg-white p-3">
        {loading ? (
          <div className="space-y-2">
            <div className="h-10 rounded-[14px] bg-[#F7F8F7]" />
            <div className="h-10 rounded-[14px] bg-[#F7F8F7]" />
          </div>
        ) : papers.length ? (
          papers.map((paper) => (
            <div key={paper.paper_id} className="rounded-[16px] border border-[#FAFBFA] bg-[#FAFBFA] p-3">
              <div className="text-sm font-semibold text-[#111827]">{paper.title}</div>
              <div className="mt-1 flex flex-wrap items-center gap-2 text-[12px] text-[#6B7280]">
                <span>{paper.upload_date}</span>
                <span>{paper.chunks_indexed} chunks</span>
              </div>
            </div>
          ))
        ) : (
          <div className="rounded-[16px] bg-[#FAFBFA] p-3 text-sm text-[#6B7280]">No papers available yet.</div>
        )}
      </div>
    </div>
  );
}
