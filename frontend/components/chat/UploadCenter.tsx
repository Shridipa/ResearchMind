"use client";

import { Upload } from "lucide-react";
import { FileChip } from "./FileChip";
import { UploadProgress } from "./UploadProgress";

interface UploadCenterProps {
  onClickUpload: () => void;
  uploadedFiles: { id: string; name: string; progress: number; status: string; message: string }[];
  progressLines: string[];
  isUploading: boolean;
}

export function UploadCenter({ onClickUpload, uploadedFiles, progressLines, isUploading }: UploadCenterProps) {
  return (
    <div className="mx-auto w-full max-w-xl">
      {/* Upload section */}
      <div className="rounded-xl border border-slate-200 bg-slate-50 px-5 py-4 text-center">
        <div className="mb-2 flex justify-center">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-emerald-100 text-emerald-700">
            <Upload size={16} />
          </div>
        </div>
        <h3 className="mb-1 text-base font-semibold text-slate-900">Upload Research Papers</h3>
        <p className="mb-3 text-sm text-slate-500">Analyze PDFs with grounded AI retrieval.</p>

        <button
          onClick={onClickUpload}
          className="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-base font-semibold text-white transition hover:bg-emerald-700 active:scale-95"
        >
          Upload Documents
        </button>
        <p className="mt-2 text-sm text-slate-400">PDF • DOCX • TXT • CSV</p>
      </div>

      {/* File chips */}
      {uploadedFiles.length > 0 && (
        <div className="mt-3 flex flex-wrap justify-center gap-2">
          {uploadedFiles.map((f) => (
            <FileChip key={f.id} name={f.name} done={f.status === "complete"} />
          ))}
        </div>
      )}

      {/* Upload progress */}
      {isUploading && (
        <div className="mt-3">
          <UploadProgress lines={progressLines} />
        </div>
      )}
    </div>
  );
}
