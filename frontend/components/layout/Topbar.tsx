"use client";
import { Book } from "lucide-react";

const NAV_ITEMS = ["Dashboard", "Papers", "Benchmarks", "Settings"];

interface TopbarProps {
  active: string;
  onChange: (tab: string) => void;
}

export function Topbar({ active, onChange }: TopbarProps) {
  return (
    <header className="mb-10 flex flex-col gap-4 pt-7 md:mb-14 md:flex-row md:items-center md:justify-between">
      <div className="flex items-center gap-3">
        <div className="flex h-[34px] w-[34px] items-center justify-center rounded-[9px] border border-[#29A662] bg-[rgba(41,166,98,0.1)] text-[#29A662]">
          <Book size={18} />
        </div>
        <span className="text-xs font-bold uppercase tracking-[0.2em] text-[#29A662]">
          ResearchMind AI
        </span>
      </div>

      <nav className="flex w-full gap-0.5 overflow-x-auto rounded-full border border-[#1A3B25] bg-[#13311E] p-1 md:w-auto">
        {NAV_ITEMS.map((item) => (
          <button
            key={item}
            onClick={() => onChange(item)}
            className={`shrink-0 rounded-full px-[18px] py-1.5 text-xs font-medium transition-all ${
              active === item
                ? "bg-[rgba(41,166,98,0.15)] text-[#3BBA75]"
                : "text-[#829987] hover:text-[#FFFFFF]"
            }`}
          >
            {item}
          </button>
        ))}
      </nav>
    </header>
  );
}
