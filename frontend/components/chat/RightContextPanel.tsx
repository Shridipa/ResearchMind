"use client";

import { useState } from "react";
import { FileText, Database, Settings2, Link } from "lucide-react";

export function RightContextPanel() {
  const [activeTab, setActiveTab] = useState("Sources");

  const TABS = [
    { id: "Sources", icon: Link },
    { id: "Papers", icon: FileText },
    { id: "Benchmarks", icon: Database },
    { id: "Settings", icon: Settings2 },
  ];

  return (
    <div className="flex h-full w-[280px] shrink-0 flex-col border-l border-slate-200 bg-slate-50">
      <div className="flex h-16 items-center px-4 border-b border-slate-200">
        <div className="flex w-full rounded-lg bg-slate-200/50 p-1">
          {TABS.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex flex-1 items-center justify-center rounded-md py-1.5 text-sm font-medium transition ${
                  isActive ? "bg-white text-slate-900 shadow-sm" : "text-slate-500 hover:text-slate-700"
                }`}
                title={tab.id}
              >
                <Icon size={16} />
              </button>
            );
          })}
        </div>
      </div>
      
      <div className="flex flex-1 flex-col items-center justify-center p-6 text-center text-base text-slate-500">
        <div className="mb-4 rounded-full bg-slate-200/50 p-3">
          <Link size={24} className="text-slate-400" />
        </div>
        <p>Sources appear here after grounded responses.</p>
      </div>
    </div>
  );
}
