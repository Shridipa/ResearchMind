"use client";

export function EmptyConversation({ message }: { message?: string }) {
  return (
    <div className="flex h-full min-h-[220px] flex-col items-center justify-center text-center text-slate-500">
      <p className="text-lg font-medium text-slate-700">{message ?? "No conversation yet"}</p>
      <p className="mt-2 text-sm">Upload a paper to start a grounded session, or ask a research question.</p>
    </div>
  );
}
