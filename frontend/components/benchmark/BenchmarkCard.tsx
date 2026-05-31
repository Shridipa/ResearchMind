"use client";

interface BenchmarkCardProps {
  label: string;
  value: string;
  delta?: string;
}

export function BenchmarkCard({ label, value, delta }: BenchmarkCardProps) {
  return (
    <div className="rounded-[18px] border border-[#E5E7EB] bg-white p-4 text-sm text-[#111827]">
      <div className="text-xs uppercase tracking-[0.2em] text-[#6B7280]">{label}</div>
      <div className="mt-2 text-lg font-semibold">{value}</div>
      {delta ? <div className="mt-1 text-[12px] text-[#4B5563]">{delta}</div> : null}
    </div>
  );
}
