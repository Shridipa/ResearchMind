import { SuggestionPills } from "./SuggestionPills";

interface WelcomeStateProps {
  onSuggestionClick?: (text: string) => void;
}

export function WelcomeState({ onSuggestionClick }: WelcomeStateProps) {
  return (
    <div className="flex max-h-[240px] w-full max-w-2xl flex-col items-center text-center">
      <h1 className="mb-1.5 text-3xl font-bold tracking-tight text-slate-900">ResearchMind AI</h1>
      <p className="mb-3 max-w-lg text-base text-slate-500">
        Grounded research conversations for academic workflows.
      </p>

      <ul className="mb-4 flex flex-col items-start gap-1 text-base text-slate-600">
        <li className="flex items-center gap-2">
          <span className="text-emerald-600">•</span>
          Analyze research papers with grounded retrieval
        </li>
        <li className="flex items-center gap-2">
          <span className="text-emerald-600">•</span>
          Ask questions across PDFs with citation-aware answers
        </li>
        <li className="flex items-center gap-2">
          <span className="text-emerald-600">•</span>
          Generate literature reviews and compare methodologies
        </li>
      </ul>

      <SuggestionPills onSelect={onSuggestionClick} />
    </div>
  );
}
