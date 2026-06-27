'use client'

import { useEffect, useState, useCallback } from 'react'
import Link from 'next/link'
import {
  FileText, Search, Cpu, Users, Upload, Activity, ArrowUpRight,
  Zap, AlertCircle, HardDrive, Clock, RefreshCw,
} from 'lucide-react'
import { motion } from 'framer-motion'
import {
  AreaChart, Area, XAxis, YAxis, ResponsiveContainer, Tooltip, CartesianGrid,
} from 'recharts'
import { useAppStore, DEMO_WORKSPACE_ID } from '@/store/appStore'
import {
  getDashboardMetrics, getDashboardActivity, getDashboardJobs, getSystemActivity, retryJob,
  type IngestionJob,
} from '@/lib/enterprise-api'

function StatusBadge({ status }: { status: string }) {
  const map: Record<string, string> = {
    COMPLETED: 'badge-completed', SEARCH_READY: 'badge-completed',
    EMBEDDING: 'badge-processing', CHUNKING: 'badge-processing', EXTRACTING: 'badge-processing',
    INDEXING: 'badge-processing', PROCESSING: 'badge-processing', QUEUED: 'badge-processing',
    UPLOADING: 'badge-processing',
    PENDING: 'badge-pending', FAILED: 'badge-failed',
  }
  return <span className={`badge ${map[status] ?? 'badge-pending'}`}>{status}</span>
}

export default function DashboardPage() {
  const { accessToken, user, ingestionJobs, liveActivity, upsertJob, connectWebSocket } = useAppStore()
  const [time, setTime] = useState(new Date())
  const [mounted, setMounted] = useState(false)
  const [metrics, setMetrics] = useState<Record<string, unknown>>({})
  const [chartData, setChartData] = useState<Array<{ time: string; docs: number; research: number }>>([])
  const [jobs, setJobs] = useState<IngestionJob[]>([])
  const [activityFeed, setActivityFeed] = useState<Array<{ action: string; message: string; user: string; timestamp: string }>>([])
  const [loading, setLoading] = useState(true)

  const wsId = user?.workspaceId ?? DEMO_WORKSPACE_ID
  const firstName = user?.firstName ?? 'Researcher'

  const loadData = useCallback(async () => {
    if (!accessToken) return
    try {
      const [m, act, j, sys] = await Promise.all([
        getDashboardMetrics(accessToken),
        getDashboardActivity(accessToken),
        getDashboardJobs(accessToken),
        getSystemActivity(accessToken),
      ])
      setMetrics(m)
      setChartData(act.chart)
      setJobs(j.jobs)
      j.jobs.forEach(job => upsertJob({
        jobId: job.id,
        documentId: job.document_id,
        documentName: job.document_name,
        status: job.status,
        progress: job.progress,
        workspaceId: job.workspace_id,
        errorMessage: job.error_message ?? undefined,
      }))
      setActivityFeed([...liveActivity.map(a => ({ action: a.action, message: a.message, user: a.user, timestamp: a.timestamp })), ...act.recent.map(r => ({ action: r.action, message: r.message, user: r.user, timestamp: r.timestamp }))].slice(0, 20))
    } catch {
      /* backend may be starting */
    } finally {
      setLoading(false)
    }
  }, [accessToken, upsertJob, liveActivity])

  useEffect(() => {
    setMounted(true)
    const t = setInterval(() => setTime(new Date()), 1000)
    loadData()
    const poll = setInterval(loadData, 8000)
    connectWebSocket(wsId)
    return () => { clearInterval(t); clearInterval(poll) }
  }, [loadData, wsId, connectWebSocket])

  useEffect(() => {
    if (liveActivity.length) {
      setActivityFeed(prev => [
        ...liveActivity.map(a => ({ action: a.action, message: a.message, user: a.user, timestamp: a.timestamp })),
        ...prev,
      ].slice(0, 25))
    }
  }, [liveActivity])

  const mergedJobs = jobs.map(j => {
    const live = ingestionJobs[j.id]
    return live ? { ...j, status: live.status, progress: live.progress } : j
  })

  const metricCards = [
    { label: 'Documents Today', value: String(metrics.documents_processed_today ?? '—'), icon: FileText, color: 'text-blue-400', bg: 'bg-blue-500/10' },
    { label: 'Active Jobs', value: String(metrics.active_jobs ?? '—'), icon: Cpu, color: 'text-violet-400', bg: 'bg-violet-500/10' },
    { label: 'Queue Depth', value: String(metrics.queue_depth ?? '—'), icon: Activity, color: 'text-emerald-400', bg: 'bg-emerald-500/10' },
    { label: 'Team Members', value: String(metrics.workspace_members ?? '—'), icon: Users, color: 'text-cyan-400', bg: 'bg-cyan-500/10' },
    { label: 'Storage Used', value: `${metrics.storage_used_gb ?? '—'} GB`, icon: HardDrive, color: 'text-amber-400', bg: 'bg-amber-500/10' },
    { label: 'Searches Today', value: String(metrics.search_queries_today ?? '—'), icon: Search, color: 'text-rose-400', bg: 'bg-rose-500/10' },
    { label: 'Avg Process Time', value: metrics.avg_processing_time_sec ? `${Math.round(Number(metrics.avg_processing_time_sec) / 60)}m` : '—', icon: Clock, color: 'text-indigo-400', bg: 'bg-indigo-500/10' },
    { label: 'System Health', value: 'Healthy', icon: Zap, color: 'text-emerald-400', bg: 'bg-emerald-500/10' },
  ]

  const handleRetry = async (jobId: string) => {
    if (!accessToken) return
    await retryJob(accessToken, jobId)
    loadData()
  }

  return (
    <div className="space-y-6 max-w-screen-xl">
      <div className="flex items-center justify-between animate-fade-in-up">
        <div>
          <h1 className="text-2xl font-bold text-white">
            Good {time.getHours() < 12 ? 'morning' : time.getHours() < 18 ? 'afternoon' : 'evening'}, {firstName} 👋
          </h1>
          <p className="text-white/45 text-sm mt-1">
            {mounted ? `${time.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })} · ${time.toLocaleTimeString()}` : ''}
          </p>
        </div>
        <Link href="/dashboard/documents" className="btn btn-primary">
          <Upload size={15} /> Upload Document
        </Link>
      </div>

      {loading ? (
        <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map(i => <div key={i} className="metric-card animate-pulse h-24 bg-white/5 rounded-xl" />)}
        </div>
      ) : (
        <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
          {metricCards.map((m, i) => (
            <motion.div key={m.label} className="metric-card" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.04 }}>
              <div className="flex items-center justify-between">
                <div className={`w-9 h-9 rounded-lg ${m.bg} flex items-center justify-center`}>
                  <m.icon size={17} className={m.color} />
                </div>
              </div>
              <p className="text-2xl font-bold text-white mt-2">{m.value}</p>
              <p className="text-xs text-white/40">{m.label}</p>
            </motion.div>
          ))}
        </div>
      )}

      <div className="grid grid-cols-1 xl:grid-cols-5 gap-4">
        <motion.div className="card xl:col-span-3" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center justify-between mb-5">
            <div>
              <h2 className="font-semibold text-white text-sm">Platform Activity</h2>
              <p className="text-white/40 text-xs mt-0.5">Documents ingested vs research sessions (24h)</p>
            </div>
            <span className="badge badge-completed"><span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" /> Live</span>
          </div>
          <ResponsiveContainer width="100%" height={180}>
            <AreaChart data={chartData.length ? chartData : [{ time: '—', docs: 0, research: 0 }]}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
              <XAxis dataKey="time" tick={{ fontSize: 10, fill: 'rgba(255,255,255,0.3)' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 10, fill: 'rgba(255,255,255,0.3)' }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ background: 'rgb(24,24,32)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 8, fontSize: 12 }} />
              <Area type="monotone" dataKey="docs" name="Documents" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.15} strokeWidth={2} dot={false} />
              <Area type="monotone" dataKey="research" name="Research" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.15} strokeWidth={2} dot={false} />
            </AreaChart>
          </ResponsiveContainer>
        </motion.div>

        <motion.div className="card xl:col-span-2 flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-white text-sm">Ingestion Pipeline</h2>
            <button onClick={loadData} className="text-white/30 hover:text-white/60"><RefreshCw size={14} /></button>
          </div>
          <div className="flex flex-col gap-3 flex-1 max-h-64 overflow-y-auto">
            {mergedJobs.length === 0 ? (
              <p className="text-xs text-white/30 text-center py-8">No active jobs — upload a document to start</p>
            ) : mergedJobs.map(job => (
              <div key={job.id} className="space-y-1.5">
                <div className="flex items-center justify-between gap-2">
                  <p className="text-xs text-white/70 truncate flex-1">{job.document_name}</p>
                  <StatusBadge status={job.status} />
                </div>
                {job.status !== 'PENDING' && job.status !== 'FAILED' && (
                  <div className="progress-bar"><div className="progress-fill" style={{ width: `${job.progress}%` }} /></div>
                )}
                {job.status === 'FAILED' && (
                  <button onClick={() => handleRetry(job.id)} className="flex items-center gap-1 text-rose-400 text-[10px] hover:underline">
                    <AlertCircle size={10} /> Retry processing
                  </button>
                )}
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Live System Activity */}
      <motion.div className="card">
        <div className="flex items-center gap-2 mb-4">
          <Activity size={15} className="text-blue-400" />
          <h2 className="font-semibold text-white text-sm">Live System Activity</h2>
        </div>
        <div className="font-mono text-[11px] space-y-1 max-h-48 overflow-y-auto">
          {activityFeed.length === 0 ? (
            <p className="text-white/30">Waiting for events…</p>
          ) : activityFeed.map((e, i) => (
            <div key={i} className="flex gap-3 text-white/50">
              <span className="text-white/25 shrink-0">{new Date(e.timestamp).toLocaleTimeString()}</span>
              <span className="text-blue-400/70 shrink-0 w-24 truncate">{e.action}</span>
              <span className="truncate">{e.message}</span>
            </div>
          ))}
        </div>
      </motion.div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {[
          { label: 'New Research Session', icon: Zap, href: '/dashboard/search', color: 'text-blue-400' },
          { label: 'Upload Batch', icon: Upload, href: '/dashboard/documents', color: 'text-violet-400' },
          { label: 'Global Search', icon: Search, href: '/dashboard/search', color: 'text-cyan-400' },
          { label: 'View Analytics', icon: Activity, href: '/dashboard/analytics', color: 'text-emerald-400' },
        ].map(action => (
          <Link key={action.label} href={action.href} className="card card-sm flex items-center gap-3 glass-hover group">
            <action.icon size={16} className={action.color} />
            <span className="text-xs font-medium text-white/65 group-hover:text-white/90">{action.label}</span>
            <ArrowUpRight size={12} className="ml-auto text-white/20 group-hover:text-white/50" />
          </Link>
        ))}
      </div>
    </div>
  )
}
