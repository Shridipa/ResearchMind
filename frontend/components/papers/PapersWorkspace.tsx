"use client";

import { useEffect, useMemo, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import {
  deletePaper,
  getPaper,
  listPapers,
  PaperRecord,
  PaperSearchResult,
  runPaperAction,
  searchPapers,
  summarizePaper,
} from "@/lib/api";
import { PaperCard } from "./PaperCard";
import { PaperDetailPanel } from "./PaperDetailPanel";
import { PapersTable } from "./PapersTable";
import { SearchBar } from "../ui/SearchBar";

interface UploadedFileState {
  id: string;
  name: string;
  progress: number;
  status: "uploading" | "indexing" | "complete" | "error";
  message: string;
}

interface PapersWorkspaceProps {
  onTriggerUpload?: () => void;
  uploadedFiles?: UploadedFileState[];
  progressLines?: string[];
  isUploading?: boolean;
  onRetryUpload?: (id: string) => void;
  onRemoveUpload?: (id: string) => void;
  onRequestReupload?: (id: string) => void;
}

export function PapersWorkspace({
  onTriggerUpload,
  uploadedFiles = [],
  progressLines = [],
  isUploading = false,
}: PapersWorkspaceProps) {
  const [papers, setPapers] = useState<PaperRecord[]>([]);
  const [selected, setSelected] = useState<PaperRecord | null>(null);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<PaperSearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState("");
  const [runningAction, setRunningAction] = useState("");
  const [actionResult, setActionResult] = useState("");
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    async function load() {
      setIsLoading(true);
      try {
        const nextPapers = await listPapers();
        setPapers(nextPapers);
        setSelected(nextPapers[0] ?? null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Could not load papers.");
      } finally {
        setIsLoading(false);
      }
    }
    load();
  }, []);

  const paperMap = useMemo(() => new Map(papers.map((paper) => [paper.paper_id, paper])), [papers]);

  async function selectPaper(paper: PaperRecord) {
    setActionResult("");
    try {
      setSelected(await getPaper(paper.paper_id));
    } catch {
      setSelected(paper);
    }
  }

  async function onSearch() {
    if (query.trim().length < 2) return;
    setIsSearching(true);
    setError("");
    try {
      setResults(await searchPapers(query));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Search failed.");
    } finally {
      setIsSearching(false);
    }
  }

  async function onAction(action: string) {
    if (!selected) return;
    setRunningAction(action);
    setActionResult("");
    try {
      if (action === "summarize") {
        const response = await summarizePaper(selected.paper_id);
        const refreshed = await getPaper(selected.paper_id);
        setSelected(refreshed);
        setPapers((items) => items.map((item) => (item.paper_id === refreshed.paper_id ? refreshed : item)));
        setActionResult(`Summary generated from ${response.sources?.length ?? 0} cited chunks.`);
      } else {
        const response = await runPaperAction(action, selected.paper_id);
        setActionResult(`${response.action.replaceAll("_", " ")} is ready.`);
      }
    } catch (err) {
      setActionResult(err instanceof Error ? err.message : "Action failed.");
    } finally {
      setRunningAction("");
    }
  }

  async function onDelete(paperId: string) {
    if (!window.confirm("Delete this paper and all indexed chunks? This cannot be undone.")) {
      return;
    }
    setIsDeleting(true);
    setActionResult("");
    try {
      await deletePaper(paperId);
      const remaining = papers.filter((paper) => paper.paper_id !== paperId);
      setPapers(remaining);
      setResults((items) => items.filter((item) => item.paper_id !== paperId));
      setSelected(remaining[0] ?? null);
      setActionResult("Paper removed. Index and metadata refreshed.");
    } catch (err) {
      setActionResult(err instanceof Error ? err.message : "Delete failed.");
    } finally {
      setIsDeleting(false);
    }
  }

  return (
    <section className="space-y-5">
      <div className="flex flex-col justify-between gap-4 rounded-[22px] border border-[#DDE5DF] bg-white p-6 shadow-sm md:flex-row md:items-end">
        <div>
          <div className="text-[11px] font-bold uppercase tracking-[0.18em] text-[#2D6A4F]">Research Workspace</div>
          <h1 className="mt-2 text-3xl font-bold text-[#0F2916]">Papers</h1>
          <p className="mt-2 max-w-2xl text-sm text-[#5B7361]">
            Inspect indexed PDFs, search across paper evidence, and launch grounded AI research actions.
          </p>
        </div>
        <div className="flex flex-col items-start gap-3 md:items-end">
          <button
            type="button"
            onClick={onTriggerUpload}
            disabled={!onTriggerUpload}
            className="inline-flex items-center justify-center rounded-2xl bg-emerald-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Upload PDF
          </button>
          <p className="text-xs text-slate-500">
            Drag and drop a PDF, or click Upload PDF to browse files.
          </p>
          {isUploading && (
            <span className="rounded-2xl bg-emerald-50 px-3 py-2 text-xs font-semibold text-emerald-700">
              Upload in progress…
            </span>
          )}
        </div>
        <div className="grid grid-cols-3 gap-2 text-center">
          <div className="rounded-[12px] bg-[#F3F6F4] px-4 py-3">
            <div className="text-lg font-bold text-[#0F2916]">{papers.length}</div>
            <div className="text-[11px] text-[#5B7361]">Papers</div>
          </div>
          <div className="rounded-[12px] bg-[#F3F6F4] px-4 py-3">
            <div className="text-lg font-bold text-[#0F2916]">
              {papers.reduce((sum, paper) => sum + paper.chunks_indexed, 0)}
            </div>
            <div className="text-[11px] text-[#5B7361]">Chunks</div>
          </div>
          <div className="rounded-[12px] bg-[#F3F6F4] px-4 py-3">
            <div className="text-lg font-bold text-[#0F2916]">{papers.filter((paper) => paper.status === "indexed").length}</div>
            <div className="text-[11px] text-[#5B7361]">Indexed</div>
          </div>
        </div>
      </div>

      <SearchBar value={query} onChange={setQuery} onSubmit={onSearch} isSearching={isSearching} />

      {error && <div className="rounded-[12px] border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}

      {isLoading ? (
        <div className="grid gap-4 lg:grid-cols-[1fr_420px]">
          <div className="h-[360px] animate-pulse rounded-[18px] bg-[#E8EFEA]" />
          <div className="h-[520px] animate-pulse rounded-[18px] bg-[#E8EFEA]" />
        </div>
      ) : (
        <div className="grid gap-5 lg:grid-cols-[1fr_520px]">
          <div className="space-y-5">
            <AnimatePresence>
              {results.length > 0 && (
                <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="space-y-3">
                  <div className="text-xs font-bold uppercase tracking-[0.16em] text-[#5B7361]">Top Semantic Matches</div>
                  <div className="grid gap-3 md:grid-cols-2">
                    {results.map((result) => (
                      <PaperCard
                        key={result.paper_id}
                        paper={result}
                        isSelected={selected?.paper_id === result.paper_id}
                        onClick={() => selectPaper(paperMap.get(result.paper_id) ?? result)}
                      />
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {papers.length ? (
              <div className="overflow-x-auto">
                <div className="min-w-[760px]">
                  <PapersTable papers={papers} selectedId={selected?.paper_id} onSelect={selectPaper} />
                </div>
              </div>
            ) : (
              <div className="rounded-[18px] border border-dashed border-[#CFE0D5] bg-white p-10 text-center text-sm text-[#5B7361]">
                Upload a PDF from the dashboard to build your paper workspace.
              </div>
            )}
          </div>

          {(uploadedFiles.length > 0 || progressLines.length > 0) && (
            <div className="space-y-4 rounded-[18px] border border-[#DDE5DF] bg-[#F8FBF7] p-4">
              <div className="text-sm font-semibold text-slate-800">Upload progress</div>
              <div className="space-y-2 text-sm text-slate-600">
                {uploadedFiles.map((file) => (
                  <div key={file.id} className="flex items-center justify-between gap-3 rounded-2xl bg-white px-4 py-3 shadow-sm">
                    <div className="flex-1">
                      <div className="font-medium text-slate-900">{file.name}</div>
                      <div className="text-xs text-slate-500">{file.message}</div>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="text-xs font-semibold text-slate-700">{file.progress}%</div>
                      {file.status === "error" && onRetryUpload ? (
                        <button
                          onClick={() => onRetryUpload(file.id)}
                          className="rounded-lg bg-emerald-600 px-3 py-1 text-xs font-semibold text-white hover:bg-emerald-700"
                        >
                          Retry
                        </button>
                      ) : null}
                      {onRequestReupload ? (
                        <button
                          onClick={() => onRequestReupload(file.id)}
                          className="rounded-lg bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700 hover:bg-slate-200"
                        >
                          Re-upload
                        </button>
                      ) : null}
                      {onRemoveUpload ? (
                        <button
                          onClick={() => onRemoveUpload(file.id)}
                          className="rounded-lg bg-red-50 px-3 py-1 text-xs font-medium text-red-600 hover:bg-red-100"
                        >
                          Remove
                        </button>
                      ) : null}
                    </div>
                  </div>
                ))}
                {progressLines.map((line, index) => (
                  <div key={index} className="text-xs text-slate-500">{line}</div>
                ))}
              </div>
            </div>
          )}

          <PaperDetailPanel
            paper={selected}
            runningAction={runningAction}
            actionResult={actionResult}
            isDeleting={isDeleting}
            onAction={onAction}
            onDelete={onDelete}
          />
        </div>
      )}
    </section>
  );
}
