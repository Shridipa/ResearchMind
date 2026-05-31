"use client";

import { TrendingDown, TrendingUp } from "lucide-react";
import { BenchmarkMetric } from "@/lib/api";

export function MetricCard({ metric }: { metric: BenchmarkMetric }) {
  const isGoodDown = metric.name.toLowerCase().includes("hallucination") || metric.name.toLowerCase().includes("latency");
  const delta = metric.delta ?? 0;
  const positive = isGoodDown ? delta < 0 : delta > 0;
  const TrendIcon = positive ? TrendingUp : TrendingDown;

  return (
    <div className="rounded-[16px] border border-[#DDE5DF] bg-white p-4 shadow-sm">
      <div className="text-[11px] font-bold uppercase tracking-[0.12em] text-[#5B7361]">{metric.name}</div>
      <div className="mt-3 flex items-end justify-between gap-3">
        <div className="text-2xl font-bold text-[#0F2916]">
          {metric.value}
          <span className="text-sm text-[#5B7361]">{metric.unit}</span>
        </div>
        <div className={`inline-flex items-center gap-1 rounded-full px-2 py-1 text-[11px] font-bold ${
          positive ? "bg-[#EAF5EF] text-[#1B4332]" : "bg-[#FFF6E8] text-[#8A5A00]"
        }`}>
          <TrendIcon size={13} />
          {delta > 0 ? "+" : ""}
          {delta}
        </div>
      </div>
    </div>
  );
}
