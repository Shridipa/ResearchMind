"use client";

import { useEffect, useRef } from "react";
import { ArrowUp, Paperclip, Sparkles, Globe } from "lucide-react";

export type UploadedFileState = {
  id: string;
  name: string;
  progress: number;
  status: "uploading" | "indexing" | "complete" | "error";
  message: string;
};

interface ChatInputProps {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
  isBusy: boolean;
  onToggleResearch: () => void;
  researchEnabled: boolean;
  webSearchEnabled?: boolean;
  onToggleWebSearch?: () => void;
  onTriggerUpload?: () => void;
  isUploading?: boolean;
}

export function ChatInput({
  value,
  onChange,
  onSend,
  isBusy,
  onToggleResearch,
  researchEnabled,
  webSearchEnabled = false,
  onToggleWebSearch,
  onTriggerUpload,
  isUploading,
}: ChatInputProps) {
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
  }, [value]);

  const canSend = !isBusy && value.trim().length > 0;

  return (
    <div className="sticky bottom-8 z-10 shrink-0 px-4 pb-12 pt-2">
      <div className="mx-auto w-full max-w-4xl">
        <div className="rounded-2xl border border-slate-200 bg-white shadow-sm focus-within:border-emerald-300 focus-within:ring-2 focus-within:ring-emerald-100 transition-all">
          {/* Textarea row */}
          <div className="flex items-end gap-2 px-3 pt-3 pb-1">
            <button
              type="button"
              onClick={onTriggerUpload}
              disabled={isBusy}
              className="mb-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-slate-400 transition hover:bg-slate-100 hover:text-slate-600 disabled:opacity-40"
              aria-label="Attach file"
              title="Attach file"
            >
              <Paperclip size={16} />
            </button>

            <textarea
              ref={textareaRef}
              name="chat-input"
              rows={1}
              value={value}
              onChange={(e) => onChange(e.target.value)}
              placeholder="Ask a research question..."
              disabled={isBusy}
              className="flex-1 resize-none bg-transparent py-1.5 text-base text-slate-900 placeholder-slate-400 outline-none disabled:opacity-60"
              style={{ maxHeight: "160px" }}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  if (canSend) onSend();
                }
              }}
            />

            <button
              type="button"
              onClick={onSend}
              disabled={!canSend}
              aria-label="Send message"
              title="Send message"
              className="mb-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-emerald-600 text-white transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-40"
            >
              <ArrowUp size={16} />
            </button>
          </div>

          {/* Toggles row */}
          <div className="flex items-center gap-2 border-t border-slate-100 px-3 py-2">
            <button
              type="button"
              onClick={onToggleResearch}
              className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-sm font-medium transition ${
                researchEnabled
                  ? "bg-emerald-100 text-emerald-700 ring-1 ring-emerald-200"
                  : "bg-slate-100 text-slate-500 hover:bg-slate-200 hover:text-slate-700"
              }`}
            >
              <Sparkles size={12} />
              Deep Research
            </button>

            <button
              type="button"
              onClick={onToggleWebSearch}
              className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-sm font-medium transition ${
                webSearchEnabled
                  ? "bg-blue-100 text-blue-700 ring-1 ring-blue-200"
                  : "bg-slate-100 text-slate-500 hover:bg-slate-200 hover:text-slate-700"
              }`}
            >
              <Globe size={12} />
              Web Search
            </button>

            <span className="ml-auto text-sm text-slate-400">
              {isUploading ? "Uploading…" : "Enter to send · Shift+Enter for newline"}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
