"use client";

import { create } from "zustand";

interface WorkspaceState {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  model: string;
  setModel: (model: string) => void;
}

export const useWorkspaceStore = create<WorkspaceState>((set) => ({
  activeTab: "Papers",
  setActiveTab: (tab) => set({ activeTab: tab }),
  model: "DeepSeek",
  setModel: (model) => set({ model }),
}));
