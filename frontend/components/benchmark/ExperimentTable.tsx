"use client";

import { ExperimentRecord } from "@/lib/api";

export function ExperimentTable({ experiments }: { experiments: ExperimentRecord[] }) {
  return (
    <div className="overflow-hidden rounded-[16px] border border-[#DDE5DF] bg-white shadow-sm">
      <div className="grid grid-cols-[0.7fr_1fr_1fr_0.8fr_0.6fr] gap-3 border-b border-[#E6ECE8] bg-[#F8FAF8] px-4 py-3 text-[11px] font-bold uppercase tracking-[0.12em] text-[#5B7361]">
        <div>ID</div>
        <div>Dataset</div>
        <div>Model</div>
        <div>Metric</div>
        <div>Score</div>
      </div>
      {experiments.map((experiment) => (
        <div key={experiment.experiment_id} className="grid grid-cols-[0.7fr_1fr_1fr_0.8fr_0.6fr] gap-3 border-b border-[#E6ECE8] px-4 py-3 text-sm last:border-b-0">
          <div className="font-mono text-xs text-[#1B4332]">{experiment.experiment_id}</div>
          <div className="truncate text-[#0F2916]">{experiment.dataset}</div>
          <div className="truncate text-[#3D5743]">{experiment.model}</div>
          <div className="truncate text-[#3D5743]">{experiment.metric}</div>
          <div className="font-bold text-[#0F2916]">{experiment.score}</div>
        </div>
      ))}
    </div>
  );
}
