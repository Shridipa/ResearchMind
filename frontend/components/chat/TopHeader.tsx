"use client";

import { useState } from "react";
import { Settings, ChevronDown, Check } from "lucide-react";
import { useWorkspaceStore } from "@/store/useWorkspaceStore";

const MODELS = ["DeepSeek", "GPT-4o", "Claude 3.5 Sonnet", "Gemini 1.5 Pro"];

export function TopHeader() {
  const model = useWorkspaceStore((s) => s.model);
  const setModel = useWorkspaceStore((s) => s.setModel);
  const [open, setOpen] = useState(false);

  return (
    <div className="relative flex h-14 w-full shrink-0 items-center justify-between border-b border-slate-100 bg-white px-5">
      <span className="text-base font-semibold tracking-tight text-slate-900">ResearchMind AI</span>

      <div className="flex items-center gap-3">
        {/* Model selector */}
        <div className="relative">
          <button
            onClick={() => setOpen((v) => !v)}
            className="flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 transition hover:border-slate-300 hover:bg-slate-50"
          >
            {model}
            <ChevronDown size={13} className={`transition-transform ${open ? "rotate-180" : ""}`} />
          </button>

          {open && (
            <div className="absolute right-0 top-full z-30 mt-1.5 min-w-[180px] overflow-hidden rounded-xl border border-slate-200 bg-white py-1 shadow-lg">
              {MODELS.map((m) => (
                <button
                  key={m}
                  onClick={() => { setModel(m); setOpen(false); }}
                  className="flex w-full items-center gap-2 px-3.5 py-2 text-left text-sm text-slate-700 transition hover:bg-slate-50"
                >
                  <span className="flex-1">{m}</span>
                  {model === m && <Check size={13} className="text-emerald-600" />}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Settings */}
        <button
          className="flex h-8 w-8 items-center justify-center rounded-lg text-slate-400 transition hover:bg-slate-100 hover:text-slate-600"
          aria-label="Settings"
          title="Settings"
        >
          <Settings size={17} />
        </button>
      </div>
    </div>
  );
}
