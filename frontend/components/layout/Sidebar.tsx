"use client";

import { useState } from "react";
import {
  Leaf,
  FileText,
  ChevronLeft,
  ChevronRight,
  BookOpen,
  BarChart2,
  Upload,
} from "lucide-react";

const NAV_ITEMS = [
  { label: "Papers", icon: FileText },
  { label: "Literature", icon: BookOpen },
  { label: "Benchmarks", icon: BarChart2 },
];

interface SidebarProps {
  activeTab: string;
  onSelectTab: (value: string) => void;
  onUpload?: () => void; // Optional upload callback prop
}

export function Sidebar({ activeTab, onSelectTab, onUpload }: SidebarProps) {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside
      className={`relative flex h-full flex-col shrink-0 border-r border-slate-200 bg-white transition-all duration-200 ${
        collapsed ? "w-[60px]" : "w-[240px]"
      }`}
    >
      {/* Logo */}
      <div className="flex h-16 items-center justify-between gap-2 border-b border-slate-100 px-3">
        {!collapsed && (
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-emerald-100">
              <Leaf size={15} className="text-emerald-700" />
            </div>
            <div className="min-w-0">
              <p className="truncate text-base font-semibold leading-tight text-slate-900">ResearchMind</p>
              <p className="truncate text-sm leading-tight text-slate-400">AI Copilot</p>
            </div>
          </div>
        )}
        {collapsed && (
          <div className="flex w-full justify-center">
            <div className="flex h-7 w-7 items-center justify-center rounded-md bg-emerald-100">
              <Leaf size={15} className="text-emerald-700" />
            </div>
          </div>
        )}
        <button
          type="button"
          onClick={() => setCollapsed((v) => !v)}
          className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg text-slate-400 transition hover:bg-slate-100 hover:text-slate-600"
          aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? <ChevronRight size={15} /> : <ChevronLeft size={15} />}
        </button>
      </div>

      <div className="flex flex-1 flex-col gap-4 overflow-y-auto p-2 pt-3">
        {/* Nav items */}
        <div className={`space-y-0.5`}>
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const active = activeTab === item.label;
            return (
              <button
                key={item.label}
                onClick={() => onSelectTab(item.label)}
                title={item.label}
                className={`flex w-full items-center gap-2.5 rounded-lg px-2.5 py-2 text-base font-medium transition ${
                  active
                    ? "bg-emerald-50 text-emerald-700"
                    : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
                } ${collapsed ? "justify-center" : ""}`}
              >
                <Icon size={16} className={active ? "text-emerald-600" : "text-slate-400"} />
                {!collapsed && item.label}
              </button>
            );
          })}
        </div>
        <div className="mt-auto px-2">
          <button
            type="button"
            onClick={onUpload}
            className="flex w-full items-center justify-center gap-2 rounded-2xl bg-emerald-50 px-3 py-3 text-sm font-semibold text-emerald-700 transition hover:bg-emerald-100"
            disabled={!onUpload}
          >
            <Upload size={16} />
            {!collapsed && "Upload PDF"}
          </button>
        </div>
      </div>
    </aside>
  );
}
