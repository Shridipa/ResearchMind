"use client";

import { Area, AreaChart, Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { ChartPoint } from "@/lib/api";

interface BenchmarkChartProps {
  title: string;
  data: ChartPoint[];
  type?: "area" | "bar";
}

export function BenchmarkChart({ title, data, type = "area" }: BenchmarkChartProps) {
  return (
    <div className="rounded-[16px] border border-[#DDE5DF] bg-white p-4 shadow-sm">
      <div className="mb-4 text-sm font-bold text-[#0F2916]">{title}</div>
      <div className="h-[230px]">
        <ResponsiveContainer width="100%" height="100%">
          {type === "area" ? (
            <AreaChart data={data}>
              <CartesianGrid stroke="#E6ECE8" strokeDasharray="3 3" />
              <XAxis dataKey="label" tick={{ fill: "#5B7361", fontSize: 11 }} />
              <YAxis tick={{ fill: "#5B7361", fontSize: 11 }} />
              <Tooltip />
              <Area type="monotone" dataKey="value" stroke="#2D6A4F" fill="#DCEFE4" strokeWidth={2} />
            </AreaChart>
          ) : (
            <BarChart data={data}>
              <CartesianGrid stroke="#E6ECE8" strokeDasharray="3 3" />
              <XAxis dataKey="label" tick={{ fill: "#5B7361", fontSize: 11 }} />
              <YAxis tick={{ fill: "#5B7361", fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="value" fill="#2D6A4F" radius={[6, 6, 0, 0]} />
              <Bar dataKey="secondary" fill="#74C69D" radius={[6, 6, 0, 0]} />
            </BarChart>
          )}
        </ResponsiveContainer>
      </div>
    </div>
  );
}
