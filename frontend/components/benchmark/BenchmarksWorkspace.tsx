"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { BenchmarkResponse, ExperimentRecord, getBenchmarks, getExperiments, runEvaluation } from "@/lib/api";
import { BenchmarkChart } from "./BenchmarkChart";
import { EvaluationPanel } from "./EvaluationPanel";
import { ExperimentTable } from "./ExperimentTable";
import { MetricCard } from "./MetricCard";

export function BenchmarksWorkspace() {
  const [benchmarks, setBenchmarks] = useState<BenchmarkResponse | null>(null);
  const [experiments, setExperiments] = useState<ExperimentRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      setIsLoading(true);
      try {
        const [benchmarkData, experimentData] = await Promise.all([getBenchmarks(), getExperiments()]);
        setBenchmarks(benchmarkData);
        setExperiments(experimentData);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Could not load benchmarks.");
      } finally {
        setIsLoading(false);
      }
    }
    load();
  }, []);

  async function onEvaluate() {
    setIsEvaluating(true);
    try {
      const response = await runEvaluation();
      setExperiments((items) => [response.experiment, ...items]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Evaluation failed.");
    } finally {
      setIsEvaluating(false);
    }
  }

  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-3">
        {Array.from({ length: 6 }).map((_, index) => (
          <div key={index} className="h-28 animate-pulse rounded-[16px] bg-[#E8EFEA]" />
        ))}
      </div>
    );
  }

  if (!benchmarks) {
    return <div className="rounded-[12px] border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>;
  }

  return (
    <section className="space-y-5">
      <div className="rounded-[22px] border border-[#DDE5DF] bg-white p-6 shadow-sm">
        <div className="text-[11px] font-bold uppercase tracking-[0.18em] text-[#2D6A4F]">Evaluation Dashboard</div>
        <h1 className="mt-2 text-3xl font-bold text-[#0F2916]">Benchmarks</h1>
        <p className="mt-2 max-w-3xl text-sm text-[#5B7361]">
          Track retrieval quality, hallucination risk, model tradeoffs, and experiment outcomes for the RAG system.
        </p>
      </div>

      {error && <div className="rounded-[12px] border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {benchmarks.metrics.map((metric, index) => (
          <motion.div key={metric.name} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.04 }}>
            <MetricCard metric={metric} />
          </motion.div>
        ))}
      </div>

      <div className="grid gap-5 xl:grid-cols-[1fr_420px]">
        <div className="space-y-5">
          <div className="grid gap-5 md:grid-cols-2">
            <BenchmarkChart title="Latency Trend" data={benchmarks.latency_trends} />
            <BenchmarkChart title="Hallucination Reduction" data={benchmarks.hallucination_reduction} type="bar" />
          </div>
          <BenchmarkChart title="Chunking Strategy Comparison" data={benchmarks.chunking_strategies} type="bar" />
          <div className="overflow-x-auto">
            <div className="min-w-[760px]">
              <ExperimentTable experiments={experiments} />
            </div>
          </div>
        </div>
        <EvaluationPanel
          models={benchmarks.embedding_models}
          heatmap={benchmarks.confidence_heatmap}
          onEvaluate={onEvaluate}
          isEvaluating={isEvaluating}
        />
      </div>
    </section>
  );
}
