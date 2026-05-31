"use client";

import { FileText } from "lucide-react";
import { motion } from "framer-motion";
import { PaperRecord, PaperSearchResult } from "@/lib/api";

interface PaperCardProps {
  paper: PaperRecord | PaperSearchResult;
  isSelected?: boolean;
  onClick: () => void;
}

export function PaperCard({ paper, isSelected, onClick }: PaperCardProps) {
  const score = "similarity_score" in paper ? paper.similarity_score : null;

  return (
    <motion.button
      layout
      whileHover={{ y: -2 }}
      onClick={onClick}
      className={`w-full rounded-[16px] border bg-white p-4 text-left shadow-sm transition-colors ${
        isSelected ? "border-[#2D6A4F]" : "border-[#DDE5DF] hover:border-[#74C69D]"
      }`}
    >
      <div className="flex items-start gap-3">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-[10px] bg-[#EAF5EF] text-[#2D6A4F]">
          <FileText size={18} />
        </div>
        <div className="min-w-0 flex-1">
          <div className="line-clamp-2 text-sm font-bold text-[#0F2916]">{paper.title}</div>
          <div className="mt-1 text-xs text-[#5B7361]">
            {paper.chunks_indexed} chunks · {paper.embedding_status}
          </div>
        </div>
        {score !== null && (
          <span className="rounded-full bg-[#EAF5EF] px-2 py-1 text-[11px] font-bold text-[#1B4332]">
            {Math.round(score * 100)}%
          </span>
        )}
      </div>
    </motion.button>
  );
}
