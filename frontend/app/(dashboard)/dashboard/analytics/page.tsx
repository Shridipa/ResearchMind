'use client'
import {
  BarChart3, TrendingUp, FileText, Search, Users, Clock,
} from 'lucide-react'
import { motion } from 'framer-motion'
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis, ResponsiveContainer,
  Tooltip, CartesianGrid, Legend,
} from 'recharts'

const throughputData = [
  { day: 'Mon', documents: 42, embeddings: 38, research: 18 },
  { day: 'Tue', documents: 58, embeddings: 52, research: 24 },
  { day: 'Wed', documents: 45, embeddings: 41, research: 21 },
  { day: 'Thu', documents: 72, embeddings: 68, research: 35 },
  { day: 'Fri', documents: 61, embeddings: 55, research: 29 },
  { day: 'Sat', documents: 28, embeddings: 25, research: 12 },
  { day: 'Sun', documents: 19, embeddings: 17, research: 8 },
]

const latencyData = [
  { hour: '00', p50: 45, p99: 120 },
  { hour: '04', p50: 38, p99: 95 },
  { hour: '08', p50: 62, p99: 180 },
  { hour: '12', p50: 78, p99: 220 },
  { hour: '16', p50: 55, p99: 145 },
  { hour: '20', p50: 48, p99: 130 },
]

const metrics = [
  { label: 'Docs Processed (7d)', value: '325', change: '+18%', icon: FileText, color: 'text-blue-400' },
  { label: 'Search Queries (7d)', value: '1,842', change: '+24%', icon: Search, color: 'text-violet-400' },
  { label: 'Active Users (7d)', value: '24', change: '+3', icon: Users, color: 'text-emerald-400' },
  { label: 'Avg Ingestion Time', value: '2.4m', change: '-12%', icon: Clock, color: 'text-cyan-400' },
]

export default function AnalyticsPage() {
  return (
    <div className="space-y-6 max-w-screen-xl">
      <div className="animate-fade-in-up">
        <div className="flex items-center gap-2.5 mb-1">
          <div className="w-6 h-6 rounded-md bg-emerald-500/20 flex items-center justify-center">
            <BarChart3 size={13} className="text-emerald-400" />
          </div>
          <h1 className="text-2xl font-bold text-white">Analytics</h1>
        </div>
        <p className="text-white/45 text-sm">Platform throughput, latency trends, and team activity</p>
      </div>

      <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
        {metrics.map((m, i) => (
          <motion.div
            key={m.label}
            className="glass-card p-4"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
          >
            <div className="flex items-center justify-between mb-3">
              <m.icon size={16} className={m.color} />
              <span className="text-xs text-emerald-400 flex items-center gap-1">
                <TrendingUp size={11} /> {m.change}
              </span>
            </div>
            <p className="text-2xl font-bold text-white">{m.value}</p>
            <p className="text-xs text-white/40 mt-1">{m.label}</p>
          </motion.div>
        ))}
      </div>

      <div className="grid xl:grid-cols-2 gap-5">
        <div className="glass-card p-5">
          <h2 className="text-sm font-semibold text-white/80 mb-4">Weekly Throughput</h2>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={throughputData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="day" tick={{ fill: 'rgba(255,255,255,0.35)', fontSize: 11 }} />
              <YAxis tick={{ fill: 'rgba(255,255,255,0.35)', fontSize: 11 }} />
              <Tooltip contentStyle={{ background: '#18181b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8 }} />
              <Legend />
              <Bar dataKey="documents" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              <Bar dataKey="embeddings" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
              <Bar dataKey="research" fill="#10b981" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="glass-card p-5">
          <h2 className="text-sm font-semibold text-white/80 mb-4">API Latency (ms)</h2>
          <ResponsiveContainer width="100%" height={240}>
            <AreaChart data={latencyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="hour" tick={{ fill: 'rgba(255,255,255,0.35)', fontSize: 11 }} />
              <YAxis tick={{ fill: 'rgba(255,255,255,0.35)', fontSize: 11 }} />
              <Tooltip contentStyle={{ background: '#18181b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8 }} />
              <Area type="monotone" dataKey="p99" stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.15} name="p99" />
              <Area type="monotone" dataKey="p50" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.15} name="p50" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
