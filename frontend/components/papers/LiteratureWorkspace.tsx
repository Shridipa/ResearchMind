"use client";

import { BookOpen, Search } from "lucide-react";
import { useState } from "react";

export function LiteratureWorkspace() {
  const [query, setQuery] = useState("");

  return (
    <section className="space-y-5">
      <div className="rounded-[22px] border border-[#DDE5DF] bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-[11px] font-bold uppercase tracking-[0.18em] text-[#2D6A4F]">Literature research</p>
            <h1 className="mt-2 text-3xl font-bold text-[#0F2916]">Literature</h1>
            <p className="mt-2 text-sm text-[#5B7361] max-w-2xl">
              Discover papers, synthesize themes, and build literature summaries for your research projects.
            </p>
          </div>
          <div className="inline-flex items-center gap-2 rounded-full bg-[#F3F6F4] px-4 py-2 text-sm font-semibold text-[#3D5743]">
            <BookOpen size={16} /> Reference library
          </div>
        </div>
      </div>

      <div className="grid gap-5 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="space-y-5 rounded-[22px] border border-[#DDE5DF] bg-white p-6 shadow-sm">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 className="text-xl font-semibold text-[#111827]">Search the literature</h2>
              <p className="mt-1 text-sm text-[#5B7361]">Enter a topic, keyword, or method to begin synthesizing research findings.</p>
            </div>
            <div className="inline-flex items-center gap-2 rounded-full bg-[#ECFDF5] px-4 py-2 text-sm font-semibold text-[#166534]">
              <Search size={16} /> Explore
            </div>
          </div>
          <div className="grid gap-4">
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search for papers, methods, or keywords..."
              className="w-full rounded-[16px] border border-[#D1D5DB] bg-[#F8FAF8] px-4 py-3 text-sm text-[#111827] outline-none transition focus:border-[#2D6A4F] focus:ring-2 focus:ring-[#D4EFE1]"
            />
            <button
              type="button"
              className="inline-flex w-fit items-center gap-2 rounded-[14px] bg-[#1F6F50] px-5 py-3 text-sm font-semibold text-white transition hover:bg-[#166534]"
            >
              <Search size={16} /> Search literature
            </button>
          </div>
        </div>

        <div className="rounded-[22px] border border-[#DDE5DF] bg-white p-6 shadow-sm">
          <h2 className="text-xl font-semibold text-[#111827]">Why literature matters</h2>
          <ul className="mt-4 space-y-3 text-sm text-[#52635C]">
            <li className="flex gap-2">
              <span className="mt-1 inline-flex h-2.5 w-2.5 rounded-full bg-[#2D6A4F]" />
              Build stronger arguments with evidence-backed sources.
            </li>
            <li className="flex gap-2">
              <span className="mt-1 inline-flex h-2.5 w-2.5 rounded-full bg-[#2D6A4F]" />
              Compare methods, datasets, and outcomes across papers.
            </li>
            <li className="flex gap-2">
              <span className="mt-1 inline-flex h-2.5 w-2.5 rounded-full bg-[#2D6A4F]" />
              Generate concise summaries for literature reviews.
            </li>
          </ul>
        </div>
      </div>
    </section>
  );
}
