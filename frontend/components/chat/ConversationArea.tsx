"use client";

import { useEffect, useRef } from "react";
import { WelcomeState } from "./WelcomeState";
import { UploadCenter } from "./UploadCenter";
import { UploadedFileState } from "./ChatInput";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  metadata?: string;
}

interface ConversationAreaProps {
  messages: Message[];
  isStreaming: boolean;
  onClickUpload: () => void;
  uploadedFiles: UploadedFileState[];
  progressLines: string[];
  isUploading: boolean;
  onSuggestionClick?: (text: string) => void;
}

function AssistantAvatar() {
  return (
    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-emerald-100 text-emerald-700 text-sm font-bold">
      R
    </div>
  );
}

function StreamingDots() {
  return (
    <div className="flex items-center gap-1 py-1">
      {[0, 1, 2].map((i) => (
        <div
          key={i}
          className="h-1.5 w-1.5 rounded-full bg-slate-400 animate-bounce"
          style={{ animationDelay: `${i * 0.15}s` }}
        />
      ))}
    </div>
  );
}

export function ConversationArea({
  messages,
  isStreaming,
  onClickUpload,
  uploadedFiles,
  progressLines,
  isUploading,
  onSuggestionClick,
}: ConversationAreaProps) {
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, isStreaming]);

  const hasMessages = messages.length > 0;

  return (
    <div className="flex flex-1 flex-col overflow-y-auto px-6 pb-0 pt-0">
      {!hasMessages ? (
        <div className="mx-auto flex min-h-full w-full max-w-4xl flex-col items-center justify-start gap-4 px-4 pb-4 pt-8">
          <WelcomeState onSuggestionClick={onSuggestionClick} />
          <div className="w-full max-w-2xl">
            <UploadCenter
              onClickUpload={onClickUpload}
              uploadedFiles={uploadedFiles}
              progressLines={progressLines}
              isUploading={isUploading}
            />
          </div>
        </div>
      ) : (
        <div className="mx-auto flex w-full max-w-2xl flex-col gap-6">
          {messages.map((msg) => (
            <div key={msg.id} className={`flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              {msg.role === "assistant" && <AssistantAvatar />}
              <div
                className={`max-w-[82%] text-base leading-7 ${
                  msg.role === "user"
                    ? "rounded-2xl rounded-tr-sm bg-slate-100 px-4 py-3 text-slate-900"
                    : "text-slate-800"
                }`}
              >
                <p className="whitespace-pre-wrap">{msg.content}</p>
                {msg.metadata && (
                  <p className="mt-2 text-sm text-slate-400">{msg.metadata}</p>
                )}
              </div>
            </div>
          ))}

          {isStreaming && (
            <div className="flex gap-3 justify-start">
              <AssistantAvatar />
              <StreamingDots />
            </div>
          )}

          <div ref={bottomRef} />
        </div>
      )}
    </div>
  );
}
