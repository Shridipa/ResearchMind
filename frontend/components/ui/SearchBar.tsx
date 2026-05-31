"use client";

import { Search } from "lucide-react";

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  isSearching?: boolean;
}

export function SearchBar({ value, onChange, onSubmit, isSearching }: SearchBarProps) {
  return (
    <div className="flex flex-col gap-3 rounded-[18px] border border-[#DDE5DF] bg-white p-3 shadow-sm md:flex-row">
      <div className="flex flex-1 items-center gap-3 rounded-[12px] border border-[#DDE5DF] bg-[#F8FAF8] px-4">
        <Search size={17} className="text-[#2D6A4F]" />
        <input
          value={value}
          onChange={(event) => onChange(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter") onSubmit();
          }}
          className="h-11 flex-1 bg-transparent text-sm text-[#0F2916] outline-none placeholder:text-[#829987]"
          placeholder="Search uploaded papers semantically..."
        />
      </div>
      <button
        onClick={onSubmit}
        disabled={isSearching || value.trim().length < 2}
        className="rounded-[10px] bg-[#1B4332] px-5 py-2.5 text-xs font-bold text-white transition-colors hover:bg-[#2D6A4F] disabled:opacity-60"
      >
        {isSearching ? "Searching" : "Search"}
      </button>
    </div>
  );
}
