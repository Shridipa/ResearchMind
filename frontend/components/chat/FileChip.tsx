"use client";

interface FileChipProps {
  name: string;
  done?: boolean;
}

export function FileChip({ name, done }: FileChipProps) {
  return (
    <div className="inline-flex items-center gap-3 rounded-full bg-emerald-50 px-3 py-2 text-sm text-slate-800 shadow-sm">
      <span className="font-medium">{name}</span>
      {done ? <span className="text-emerald-600 font-semibold">✓</span> : null}
    </div>
  );
}
