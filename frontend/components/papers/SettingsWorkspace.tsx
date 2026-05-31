"use client";

import { useState } from "react";
import { Moon, SlidersHorizontal, Sun } from "lucide-react";

export function SettingsWorkspace() {
  const [model, setModel] = useState("Grounded mock generator");
  const [embedding, setEmbedding] = useState("BGE embeddings");
  const [chunkSize, setChunkSize] = useState(900);
  const [temperature, setTemperature] = useState(0.2);
  const [depth, setDepth] = useState(5);
  const [darkMode, setDarkMode] = useState(false);

  return (
    <section className="space-y-5">
      <div className="rounded-[22px] border border-[#DDE5DF] bg-white p-6 shadow-sm">
        <div className="flex items-center gap-2 text-[11px] font-bold uppercase tracking-[0.18em] text-[#2D6A4F]">
          <SlidersHorizontal size={15} />
          System Configuration
        </div>
        <h1 className="mt-2 text-3xl font-bold text-[#0F2916]">Settings</h1>
        <p className="mt-2 max-w-3xl text-sm text-[#5B7361]">
          Tune retrieval, generation, and indexing behavior for research experiments.
        </p>
      </div>

      <div className="grid gap-5 lg:grid-cols-2">
        <div className="rounded-[18px] border border-[#DDE5DF] bg-white p-5 shadow-sm">
          <h2 className="text-lg font-bold text-[#0F2916]">Model Stack</h2>
          <div className="mt-5 space-y-4">
            <label className="block">
              <span className="text-xs font-bold uppercase tracking-[0.12em] text-[#5B7361]">Answer Model</span>
              <select value={model} onChange={(event) => setModel(event.target.value)} className="mt-2 h-11 w-full rounded-[10px] border border-[#DDE5DF] bg-[#F8FAF8] px-3 text-sm text-[#0F2916] outline-none focus:border-[#2D6A4F]">
                <option>Grounded mock generator</option>
                <option>GPT citation mode</option>
                <option>Local instruction model</option>
              </select>
            </label>
            <label className="block">
              <span className="text-xs font-bold uppercase tracking-[0.12em] text-[#5B7361]">Embedding Model</span>
              <select value={embedding} onChange={(event) => setEmbedding(event.target.value)} className="mt-2 h-11 w-full rounded-[10px] border border-[#DDE5DF] bg-[#F8FAF8] px-3 text-sm text-[#0F2916] outline-none focus:border-[#2D6A4F]">
                <option>all-MiniLM</option>
                <option>BGE embeddings</option>
                <option>E5 embeddings</option>
              </select>
            </label>
          </div>
        </div>

        <div className="rounded-[18px] border border-[#DDE5DF] bg-white p-5 shadow-sm">
          <h2 className="text-lg font-bold text-[#0F2916]">Retrieval Controls</h2>
          <div className="mt-5 space-y-5">
            <label className="block">
              <div className="flex justify-between text-xs font-bold uppercase tracking-[0.12em] text-[#5B7361]">
                <span>Chunk Size</span>
                <span>{chunkSize}</span>
              </div>
              <input type="range" min={400} max={1400} step={50} value={chunkSize} onChange={(event) => setChunkSize(Number(event.target.value))} className="mt-3 w-full accent-[#2D6A4F]" />
            </label>
            <label className="block">
              <div className="flex justify-between text-xs font-bold uppercase tracking-[0.12em] text-[#5B7361]">
                <span>Temperature</span>
                <span>{temperature.toFixed(1)}</span>
              </div>
              <input type="range" min={0} max={1} step={0.1} value={temperature} onChange={(event) => setTemperature(Number(event.target.value))} className="mt-3 w-full accent-[#2D6A4F]" />
            </label>
            <label className="block">
              <div className="flex justify-between text-xs font-bold uppercase tracking-[0.12em] text-[#5B7361]">
                <span>Retrieval Depth</span>
                <span>{depth}</span>
              </div>
              <input type="range" min={3} max={12} step={1} value={depth} onChange={(event) => setDepth(Number(event.target.value))} className="mt-3 w-full accent-[#2D6A4F]" />
            </label>
          </div>
        </div>

        <div className="rounded-[18px] border border-[#DDE5DF] bg-white p-5 shadow-sm lg:col-span-2">
          <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
            <div>
              <h2 className="text-lg font-bold text-[#0F2916]">Appearance</h2>
              <p className="mt-1 text-sm text-[#5B7361]">Switch the interface mode used for research sessions.</p>
            </div>
            <button
              onClick={() => setDarkMode((value) => !value)}
              className="inline-flex items-center gap-2 rounded-[10px] border border-[#CFE0D5] bg-[#F8FAF8] px-4 py-2 text-sm font-bold text-[#1B4332]"
            >
              {darkMode ? <Moon size={16} /> : <Sun size={16} />}
              {darkMode ? "Dark mode" : "Light mode"}
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
