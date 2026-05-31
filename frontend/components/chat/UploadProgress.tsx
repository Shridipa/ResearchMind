"use client";
import { Loader2 } from "lucide-react";

interface UploadProgressProps {
  lines: string[];
}

export function UploadProgress({ lines }: UploadProgressProps) {
  return (
    <div className="mt-3 w-full max-w-3xl rounded-md bg-white/60 p-3 text-sm text-slate-700 shadow-sm">
      <div className="flex items-center gap-2 text-slate-600">
        <Loader2 className="animate-spin" size={16} />
        <span className="font-medium">Indexing...</span>
      </div>
      <div className="mt-2 space-y-1 text-xs text-slate-600">
        {lines.map((l, i) => (
          <div key={i} className="flex items-center gap-2">
            <span className="inline-block h-2 w-2 rounded-full bg-emerald-500" />
            <span>{l}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
