const SUGGESTIONS = [
  "Summarize this paper",
  "Compare methodologies",
  "Explain this equation",
  "Find research gaps",
  "Generate literature review",
];

interface SuggestionPillsProps {
  onSelect?: (text: string) => void;
}

export function SuggestionPills({ onSelect }: SuggestionPillsProps) {
  return (
    <div className="flex flex-wrap items-center justify-center gap-2">
      {SUGGESTIONS.map((text, idx) => (
        <button
          key={idx}
          onClick={() => onSelect?.(text)}
          className="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-600 transition-all hover:border-emerald-300 hover:bg-emerald-50 hover:text-emerald-700"
        >
          {text}
        </button>
      ))}
    </div>
  );
}
