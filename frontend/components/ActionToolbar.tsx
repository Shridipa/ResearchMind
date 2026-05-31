"use client";

import { FileSearch, GitCompare, Layers, Sparkles } from "lucide-react";

const ACTIONS = [
  { id: "summarize", label: "Summarize", icon: Sparkles },
  { id: "extract-citations", label: "Citations", icon: FileSearch },
  { id: "compare", label: "Compare", icon: GitCompare },
  { id: "literature-review", label: "Review", icon: Layers },
];

interface ActionToolbarProps {
  disabled?: boolean;
  runningAction?: string;
  onAction: (action: string) => void;
}

export function ActionToolbar({ disabled, runningAction, onAction }: ActionToolbarProps) {
  return (
    <div className="flex flex-wrap gap-2">
      {ACTIONS.map((action) => {
        const Icon = action.icon;
        const isRunning = runningAction === action.id;
        return (
          <button
            key={action.id}
            type="button"
            disabled={disabled || Boolean(runningAction)}
            onClick={() => onAction(action.id)}
            className="inline-flex items-center gap-2 rounded-[10px] border border-[#CFE0D5] bg-white px-3 py-2 text-xs font-bold text-[#1B4332] transition-colors hover:border-[#74C69D] hover:bg-[#EAF5EF] disabled:cursor-not-allowed disabled:opacity-60"
          >
            <Icon size={14} />
            {isRunning ? "Running..." : action.label}
          </button>
        );
      })}
    </div>
  );
}
