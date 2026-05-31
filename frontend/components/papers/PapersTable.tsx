"use client";

import { motion } from "framer-motion";
import { PaperRecord } from "@/lib/api";

interface PapersTableProps {
  papers: PaperRecord[];
  selectedId?: string;
  onSelect: (paper: PaperRecord) => void;
}

export function PapersTable({ papers, selectedId, onSelect }: PapersTableProps) {
  return (
    <div className="overflow-hidden rounded-[18px] border border-[#DDE5DF] bg-white shadow-sm">
      <div className="grid grid-cols-[1.5fr_0.8fr_0.7fr_0.8fr_0.8fr] gap-3 border-b border-[#E6ECE8] bg-[#F8FAF8] px-4 py-3 text-[11px] font-bold uppercase tracking-[0.12em] text-[#5B7361]">
        <div>Title</div>
        <div>Upload Date</div>
        <div>Chunks</div>
        <div>Embedding</div>
        <div>State</div>
      </div>
      <div className="divide-y divide-[#E6ECE8]">
        {papers.map((paper, index) => (
          <motion.button
            key={paper.paper_id}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.04 }}
            whileHover={{ backgroundColor: "#F8FAF8" }}
            onClick={() => onSelect(paper)}
            className={`grid w-full grid-cols-[1.5fr_0.8fr_0.7fr_0.8fr_0.8fr] gap-3 px-4 py-4 text-left text-sm ${
              selectedId === paper.paper_id ? "bg-[#EAF5EF]" : "bg-white"
            }`}
          >
            <div className="min-w-0">
              <div className="truncate font-bold text-[#0F2916]">{paper.title}</div>
              <div className="truncate text-xs text-[#5B7361]">
                {paper.authors.length ? paper.authors.join(", ") : paper.filename}
              </div>
            </div>
            <div className="text-xs text-[#3D5743]">{new Date(paper.upload_date).toLocaleDateString()}</div>
            <div className="font-mono text-xs text-[#0F2916]">{paper.chunks_indexed}</div>
            <div>
              <span className="rounded-full bg-[#EAF5EF] px-2 py-1 text-[11px] font-bold text-[#1B4332]">
                {paper.embedding_status}
              </span>
            </div>
            <div className="text-xs font-bold text-[#2D6A4F]">{paper.processing_state}</div>
          </motion.button>
        ))}
      </div>
    </div>
  );
}
