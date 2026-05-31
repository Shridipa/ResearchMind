"use client";

import { DragEvent } from "react";
import { TopHeader } from "./TopHeader";
import { ConversationArea } from "./ConversationArea";
import { ChatInput } from "./ChatInput";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  metadata?: string;
}

interface UploadedFileState {
  id: string;
  name: string;
  progress: number;
  status: "uploading" | "indexing" | "complete" | "error";
  message: string;
}

interface ChatWorkspaceProps {
  messages: Message[];
  isStreaming: boolean;
  isBusy: boolean;
  question: string;
  researchEnabled: boolean;
  webSearchEnabled: boolean;
  uploadedFiles: UploadedFileState[];
  progressLines: string[];
  isUploading: boolean;
  dragActive: boolean;
  onQuestionChange: (value: string) => void;
  onSend: () => void;
  onToggleResearch: () => void;
  onToggleWebSearch: () => void;
  onTriggerUpload: () => void;
  onFilesSelected: (files: File[]) => void;
  onDragOver: (e: DragEvent<HTMLDivElement>) => void;
  onDragEnter: (e: DragEvent<HTMLDivElement>) => void;
  onDragLeave: (e: DragEvent<HTMLDivElement>) => void;
  onDrop: (e: DragEvent<HTMLDivElement>) => void;
  onSuggestionClick: (text: string) => void;
}

export function ChatWorkspace({
  messages,
  isStreaming,
  isBusy,
  question,
  researchEnabled,
  webSearchEnabled,
  uploadedFiles,
  progressLines,
  isUploading,
  dragActive,
  onQuestionChange,
  onSend,
  onToggleResearch,
  onToggleWebSearch,
  onTriggerUpload,
  onDragOver,
  onDragEnter,
  onDragLeave,
  onDrop,
  onSuggestionClick,
}: ChatWorkspaceProps) {
  return (
    <div
      className="relative flex flex-1 min-w-0 flex-col bg-white overflow-hidden"
      onDragOver={onDragOver}
      onDragEnter={onDragEnter}
      onDragLeave={onDragLeave}
      onDrop={onDrop}
    >
      {/* Compact top header */}
      <TopHeader />

      {/* Scrollable conversation */}
      <ConversationArea
        messages={messages}
        isStreaming={isStreaming}
        onClickUpload={onTriggerUpload}
        uploadedFiles={uploadedFiles}
        progressLines={progressLines}
        isUploading={isUploading}
        onSuggestionClick={onSuggestionClick}
      />

      {/* Sticky chat input */}
      <ChatInput
        value={question}
        onChange={onQuestionChange}
        onSend={onSend}
        isBusy={isBusy}
        onToggleResearch={onToggleResearch}
        researchEnabled={researchEnabled}
        webSearchEnabled={webSearchEnabled}
        onToggleWebSearch={onToggleWebSearch}
        onTriggerUpload={onTriggerUpload}
        isUploading={isUploading}
      />

      {/* Drag overlay */}
      {dragActive && (
        <div className="pointer-events-none absolute inset-0 z-20 flex items-center justify-center bg-white/80 backdrop-blur-sm">
          <div className="flex flex-col items-center gap-3 rounded-2xl border-2 border-dashed border-emerald-400 bg-emerald-50 px-12 py-10 text-center shadow-lg">
            <div className="text-3xl">📄</div>
            <p className="text-base font-semibold text-emerald-700">Drop files to analyze</p>
            <p className="text-sm text-emerald-600">PDF • DOCX • TXT • CSV</p>
          </div>
        </div>
      )}
    </div>
  );
}
