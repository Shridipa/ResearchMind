"use client";

import { useEffect, useState, useRef } from "react";
import { useWorkspaceStore } from "@/store/useWorkspaceStore";

import { SUPPORTED_UPLOAD_ACCEPT, uploadDocument, SUPPORTED_UPLOAD_EXTENSIONS } from "@/lib/upload";
import { UploadedFileState } from "@/components/chat/ChatInput";

import { Sidebar } from "./Sidebar";
import { PapersWorkspace } from "../papers/PapersWorkspace";
import { LiteratureWorkspace } from "../literature/LiteratureWorkspace";
import { BenchmarksWorkspace } from "../benchmark/BenchmarksWorkspace";

// ─── component ────────────────────────────────────────────────────────────────────

export function ResearchWorkspace() {
  const activeTab = useWorkspaceStore((s) => s.activeTab);
  const setActiveTab = useWorkspaceStore((s) => s.setActiveTab);

  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [papersRefreshKey, setPapersRefreshKey] = useState(0);

  // ── toast auto-dismiss ──
  useEffect(() => {
    if (!toastMessage) return;
    const t = window.setTimeout(() => setToastMessage(null), 4000);
    return () => window.clearTimeout(t);
  }, [toastMessage]);

  // ── file upload ──
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const uid = () => Math.random().toString(36).slice(2, 9);

  const isSupportedFile = (name: string) => {
    const ext = name.split(".").pop()?.toLowerCase() ?? "";
    return SUPPORTED_UPLOAD_EXTENSIONS.includes(ext);
  };

  const [uploadedFiles, setUploadedFiles] = useState<Array<any>>([]);
  const [progressLines, setProgressLines] = useState<string[]>([]);
  const [messages, setMessages] = useState<Array<any>>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [pendingReuploadId, setPendingReuploadId] = useState<string | null>(null);
  const [isBusy, setIsBusy] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [question, setQuestion] = useState("");
  const uploadFile = async (file: File, existingId?: string) => {
    const id = existingId ?? uid();
    const progressMsgId = uid();

    if (!existingId) {
      setUploadedFiles((prev) => [
        ...prev,
        { id, file, name: file.name, progress: 0, status: "uploading", message: "Queued…" },
      ]);
    } else {
      setUploadedFiles((prev) =>
        prev.map((f) => (f.id === id ? { ...f, file, name: file.name, progress: 0, status: "uploading", message: "Reuploading…" } : f))
      );
    }

    setMessages((prev) => [
      ...prev,
      { id: progressMsgId, role: "assistant", content: `Preparing upload for ${file.name}…` },
    ]);

    try {
      const response = await uploadDocument(file, (p) => {
        setUploadedFiles((prev) =>
          prev.map((f) =>
            f.id !== id
              ? f
              : { ...f, progress: p.percent, status: p.percent === 100 ? "indexing" : "uploading", message: p.message }
          )
        );
        setProgressLines((prev) => [
          `${file.name}: ${p.message}`,
          ...prev.filter((line) => !line.startsWith(`${file.name}:`)),
        ]);
        setMessages((prev) =>
          prev.map((m) =>
            m.id !== progressMsgId
              ? m
              : { ...m, content: `Uploading ${file.name}: ${p.percent}% — ${p.message}` }
          )
        );
      });

      setUploadedFiles((prev) =>
        prev.map((f) =>
          f.id !== id ? f : { ...f, progress: 100, status: "complete", message: `Indexed ${response.chunks_indexed} chunks` }
        )
      );
      setProgressLines((prev) => [
        `${file.name}: Indexed ${response.chunks_indexed} chunks`,
        ...prev.filter((line) => !line.startsWith(`${file.name}:`)),
      ]);
      setMessages((prev) =>
        prev.map((m) =>
          m.id !== progressMsgId
            ? m
            : { ...m, content: `✓ ${file.name} indexed — ${response.chunks_indexed} chunks ready for search.` }
        )
      );
      setToastMessage(`${file.name} indexed (${response.chunks_indexed} chunks)`);
      setPapersRefreshKey((k) => k + 1);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Upload failed.";
      setUploadedFiles((prev) =>
        prev.map((f) => (f.id !== id ? f : { ...f, status: "error", message: msg }))
      );
      setProgressLines((prev) => [
        `${file.name}: ${msg}`,
        ...prev.filter((line) => !line.startsWith(`${file.name}:`)),
      ]);
      const errId = uid();
      setMessages((prev) => [...prev, { id: errId, role: "assistant", content: `Upload failed for ${file.name}: ${msg}` }]);
      setToastMessage(`Upload failed: ${file.name}`);
    }
  };

  const handleRetryUpload = async (id: string) => {
    const entry = uploadedFiles.find((f) => f.id === id);
    if (!entry || !entry.file) {
      setToastMessage("Original file not available for retry.");
      return;
    }
    await uploadFile(entry.file, id);
  };

  const handleRemoveUpload = (id: string) => {
    setUploadedFiles((prev) => prev.filter((f) => f.id !== id));
    setProgressLines((prev) => prev.filter((l) => !l.startsWith(`${id}:`) && !l.includes(id)));
  };

  const handleRequestReupload = (id: string) => {
    setPendingReuploadId(id);
    triggerFilePicker();
  };

  const handleFilesSelected = async (files: File[]) => {
    const accepted = files.filter((f) => isSupportedFile(f.name));
    const rejected = files.filter((f) => !isSupportedFile(f.name));
    if (rejected.length) setToastMessage("Only PDF files are supported.");
    if (!accepted.length) return;
    setIsUploading(true);
    for (const f of accepted) await uploadFile(f);
    setIsUploading(false);
  };

  // ── chat ──
  type ChatResponse = { confidence?: number; unsupported_claim_risk?: number };
  const askQuestionStream = async (
    _text: string,
    _onMeta?: (m: Partial<ChatResponse>) => void,
    _onChunk?: (t: string) => void,
    _onComplete?: () => void
  ) => {
    // minimal stub for local dev — no-op
    _onComplete?.();
  };

  const sendMessage = async () => {
    if (!question.trim() || isBusy) return;

    const userMsgId = uid();
    const assistantMsgId = uid();
    const userText = question.trim();

    setMessages((prev) => [...prev, { id: userMsgId, role: "user", content: userText }]);
    setQuestion("");
    setIsBusy(true);
    setIsStreaming(true);

    // placeholder for streaming assistant message
    setMessages((prev) => [...prev, { id: assistantMsgId, role: "assistant", content: "" }]);

    try {
      let meta: Partial<ChatResponse> = {};
      await askQuestionStream(
        userText,
        (metadata) => {
          meta = { ...meta, ...metadata };
        },
        (text) => {
          setMessages((prev) =>
            prev.map((m) =>
              m.id !== assistantMsgId ? m : { ...m, content: m.content + text }
            )
          );
        },
        () => {
          const metaStr =
            meta.confidence != null
              ? `Confidence ${Math.round(meta.confidence * 100)}% · Risk ${Math.round((meta.unsupported_claim_risk ?? 0) * 100)}%`
              : undefined;
          setMessages((prev) =>
            prev.map((m) => (m.id !== assistantMsgId ? m : { ...m, metadata: metaStr }))
          );
          setIsBusy(false);
          setIsStreaming(false);
        }
      );
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Something went wrong.";
      setMessages((prev) =>
        prev.map((m) => (m.id !== assistantMsgId ? m : { ...m, content: `Error: ${msg}` }))
      );
      setIsBusy(false);
      setIsStreaming(false);
    }
  };

  // ── drag & drop ──
  const handleDragOver = (e: any) => { e.preventDefault(); setDragActive(true); };
  const handleDragEnter = (e: any) => { e.preventDefault(); setDragActive(true); };
  const handleDragLeave = (e: any) => { e.preventDefault(); setDragActive(false); };
  const handleDrop = async (e: any) => {
    e.preventDefault();
    setDragActive(false);
    if (!e.dataTransfer.files.length) return;
    await handleFilesSelected(Array.from(e.dataTransfer.files));
  };

  const triggerFilePicker = () => fileInputRef.current?.click();

  const handleFileInputChange = (e: any) => {
    if (!e.target.files) return;
    const files = Array.from(e.target.files) as File[];
    if (pendingReuploadId) {
      const f = files[0];
      if (f) {
        if (!isSupportedFile(f.name)) {
          setToastMessage("Only PDF files are supported.");
          setPendingReuploadId(null);
          e.target.value = "";
          return;
        }
        // replace existing entry and upload
        uploadFile(f, pendingReuploadId);
      }
      setPendingReuploadId(null);
    } else {
      handleFilesSelected(files);
    }
    e.target.value = "";
  };

  // ── render ──
  return (
    <div
      className="relative flex h-screen overflow-hidden bg-white"
      onDragOver={handleDragOver}
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {/* Left sidebar — 240 px */}
      <Sidebar activeTab={activeTab} onSelectTab={setActiveTab} onUpload={triggerFilePicker} />

      {/* Center workspace */}
      {activeTab === "Papers" ? (
        <div className="flex flex-1 flex-col overflow-hidden bg-white">
          <div className="flex-1 overflow-y-auto p-6">
            <PapersWorkspace
              key={papersRefreshKey}
              onTriggerUpload={triggerFilePicker}
              uploadedFiles={uploadedFiles as UploadedFileState[]}
              progressLines={progressLines}
              isUploading={isUploading}
              onRetryUpload={(id) => handleRetryUpload(id)}
              onRemoveUpload={(id) => handleRemoveUpload(id)}
              onRequestReupload={(id) => handleRequestReupload(id)}
            />
          </div>
        </div>
      ) : activeTab === "Literature" ? (
        <div className="flex flex-1 flex-col overflow-hidden bg-white">
          <LiteratureWorkspace />
        </div>
      ) : activeTab === "Benchmarks" ? (
        <div className="flex flex-1 flex-col overflow-hidden bg-white">
          <div className="flex-1 overflow-y-auto p-6">
            <BenchmarksWorkspace />
          </div>
        </div>
      ) : null}

      {/* Toast */}
      {toastMessage && (
        <div className="pointer-events-none fixed bottom-8 left-1/2 z-50 -translate-x-1/2">
          <div className="rounded-full border border-slate-200 bg-white px-5 py-3 text-sm font-medium text-slate-800 shadow-lg">
            {toastMessage}
          </div>
        </div>
      )}

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        name="files"
        multiple
        accept={SUPPORTED_UPLOAD_ACCEPT}
        className="hidden"
        onChange={handleFileInputChange}
        aria-label="Upload research files"
        title="Upload research files"
      />
    </div>
  );
}
