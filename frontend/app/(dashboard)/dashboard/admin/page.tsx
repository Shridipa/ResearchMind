'use client'
import { useState } from 'react'
import {
  Shield, Users, Activity, Server, Database,
  AlertTriangle, CheckCircle, Clock, Terminal,
  BarChart3, Cpu, HardDrive, Zap, RefreshCw,
} from 'lucide-react'
import { motion } from 'framer-motion'
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip, CartesianGrid } from 'recharts'

const queueData = [
  { queue: 'documents', active: 3, queued: 12, failed: 1 },
  { queue: 'embeddings', active: 2, queued: 8, failed: 0 },
  { queue: 'research', active: 1, queued: 5, failed: 2 },
  { queue: 'cleanup', active: 0, queued: 0, failed: 0 },
  { queue: 'notifications', active: 0, queued: 3, failed: 0 },
]

const auditLogs = [
  { id: 'al1', user: 'jane@research.ai', action: 'DOCUMENT_UPLOAD', resource: 'GPT-4 Technical Report.pdf', ip: '192.168.1.101', time: '14:32:01' },
  { id: 'al2', user: 'alex@research.ai', action: 'RESEARCH_RUN', resource: 'session-a1b2c3', ip: '192.168.1.105', time: '14:28:44' },
  { id: 'al3', user: 'admin@research.ai', action: 'PERMISSION_CHANGE', resource: 'marcus@research.ai → VIEWER', ip: '10.0.0.1', time: '13:55:12' },
  { id: 'al4', user: 'priya@research.ai', action: 'WORKSPACE_CREATE', resource: 'Drug Discovery', ip: '192.168.1.110', time: '13:20:33' },
  { id: 'al5', user: 'alex@research.ai', action: 'DOCUMENT_DELETE', resource: 'old-draft.pdf', ip: '192.168.1.105', time: '12:10:05' },
]

const ACTION_COLOR: Record<string, string> = {
  DOCUMENT_UPLOAD: 'text-blue-400',
  RESEARCH_RUN: 'text-violet-400',
  PERMISSION_CHANGE: 'text-orange-400',
  WORKSPACE_CREATE: 'text-emerald-400',
  DOCUMENT_DELETE: 'text-rose-400',
}

const systemMetrics = [
  { label: 'API Latency (p99)', value: '142ms', status: 'ok', icon: Zap },
  { label: 'Error Rate', value: '0.12%', status: 'ok', icon: AlertTriangle },
  { label: 'CPU Usage', value: '34%', status: 'ok', icon: Cpu },
  { label: 'Memory', value: '6.2 / 16 GB', status: 'ok', icon: HardDrive },
  { label: 'DB Connections', value: '48 / 100', status: 'warn', icon: Database },
  { label: 'Queue Depth', value: '28 jobs', status: 'ok', icon: Server },
]

export default function AdminPage() {
  const [activeTab, setActiveTab] = useState<'health' | 'queue' | 'audit' | 'users'>('health')

  return (
    <div className="space-y-5 max-w-screen-xl">
      {/* Header */}
      <div className="flex items-center justify-between animate-fade-in-up">
        <div>
          <div className="flex items-center gap-2.5 mb-1">
            <div className="w-6 h-6 rounded-md bg-violet-500/20 flex items-center justify-center">
              <Shield size={13} className="text-violet-400" />
            </div>
            <h1 className="text-2xl font-bold text-white">Admin Portal</h1>
          </div>
          <p className="text-white/45 text-sm">System health, queue monitoring, audit logs, and user management</p>
        </div>
        <button className="btn btn-ghost text-xs gap-1.5">
          <RefreshCw size={13} /> Refresh
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 p-1 rounded-xl bg-[rgb(18,18,23)] border border-white/5 w-fit">
        {[
          { id: 'health', label: 'System Health', icon: Activity },
          { id: 'queue', label: 'Queue Monitor', icon: Server },
          { id: 'audit', label: 'Audit Logs', icon: Terminal },
          { id: 'users', label: 'Users', icon: Users },
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-medium transition-all ${
              activeTab === tab.id ? 'bg-blue-500/20 text-blue-400' : 'text-white/40 hover:text-white/70'
            }`}
          >
            <tab.icon size={13} />
            {tab.label}
          </button>
        ))}
      </div>

      {/* System Health */}
      {activeTab === 'health' && (
        <motion.div className="space-y-4" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-3">
            {systemMetrics.map((m, i) => (
              <motion.div key={m.label} className="metric-card" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}>
                <div className="flex items-center justify-between">
                  <m.icon size={14} className="text-white/40" />
                  {m.status === 'ok'
                    ? <CheckCircle size={12} className="text-emerald-400" />
                    : <AlertTriangle size={12} className="text-orange-400" />}
                </div>
                <p className="text-sm font-bold text-white mt-2">{m.value}</p>
                <p className="text-[10px] text-white/35 leading-tight">{m.label}</p>
              </motion.div>
            ))}
          </div>

          <div className="card">
            <h2 className="font-semibold text-white text-sm mb-4">Worker Status</h2>
            <div className="space-y-3">
              {['document_worker@node1', 'embedding_worker@node1', 'embedding_worker@node2', 'research_worker@node1'].map((w, i) => (
                <div key={w} className="flex items-center gap-3">
                  <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                  <span className="text-xs text-white/65 font-mono flex-1">{w}</span>
                  <span className="badge badge-completed text-[10px]">ONLINE</span>
                  <span className="text-[10px] text-white/30">{['3 tasks', '1 task', '2 tasks', '0 tasks'][i]}</span>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      )}

      {/* Queue Monitor */}
      {activeTab === 'queue' && (
        <motion.div className="space-y-4" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <div className="card">
            <h2 className="font-semibold text-white text-sm mb-4">Queue Depth by Worker Pool</h2>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={queueData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                <XAxis dataKey="queue" tick={{ fontSize: 11, fill: 'rgba(255,255,255,0.4)' }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11, fill: 'rgba(255,255,255,0.4)' }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ background: 'rgb(24,24,32)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 8, fontSize: 12 }} />
                <Bar dataKey="active" name="Active" fill="#3b82f6" radius={[4,4,0,0]} />
                <Bar dataKey="queued" name="Queued" fill="#8b5cf6" radius={[4,4,0,0]} />
                <Bar dataKey="failed" name="Failed" fill="#fb7185" radius={[4,4,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="card">
            <table className="table">
              <thead><tr><th>Queue</th><th>Active</th><th>Queued</th><th>Failed</th><th>Status</th></tr></thead>
              <tbody>
                {queueData.map(q => (
                  <tr key={q.queue}>
                    <td className="font-mono text-xs text-blue-400">{q.queue}</td>
                    <td><span className="badge badge-processing">{q.active}</span></td>
                    <td className="text-white/60">{q.queued}</td>
                    <td>{q.failed > 0 ? <span className="badge badge-failed">{q.failed}</span> : <span className="text-white/30">—</span>}</td>
                    <td>
                      {q.active + q.queued > 0
                        ? <span className="badge badge-processing">BUSY</span>
                        : <span className="badge badge-completed">IDLE</span>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>
      )}

      {/* Audit Logs */}
      {activeTab === 'audit' && (
        <motion.div className="card" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-white text-sm">Audit Trail</h2>
            <button className="btn btn-ghost text-xs">Export CSV</button>
          </div>
          <table className="table">
            <thead><tr><th>Time</th><th>User</th><th>Action</th><th>Resource</th><th>IP</th></tr></thead>
            <tbody>
              {auditLogs.map(log => (
                <tr key={log.id}>
                  <td className="font-mono text-[11px] text-white/35">{log.time}</td>
                  <td className="text-xs text-white/65">{log.user}</td>
                  <td>
                    <span className={`text-xs font-mono font-medium ${ACTION_COLOR[log.action] ?? 'text-white/50'}`}>{log.action}</span>
                  </td>
                  <td className="text-xs text-white/50 max-w-[200px] truncate">{log.resource}</td>
                  <td className="font-mono text-[11px] text-white/30">{log.ip}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </motion.div>
      )}

      {/* Users */}
      {activeTab === 'users' && (
        <motion.div className="card" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-white text-sm">All Users</h2>
            <span className="text-xs text-white/35">4 total</span>
          </div>
          <table className="table">
            <thead><tr><th>User</th><th>Email</th><th>Role</th><th>Status</th><th>Last Active</th></tr></thead>
            <tbody>
              {[
                { name: 'Jane Doe', email: 'jane@research.ai', role: 'ORG_ADMIN', status: 'active', last: '2m ago' },
                { name: 'Alex Chen', email: 'alex@research.ai', role: 'RESEARCHER', status: 'active', last: '15m ago' },
                { name: 'Priya Singh', email: 'priya@research.ai', role: 'RESEARCHER', status: 'active', last: '1h ago' },
                { name: 'Marcus Wu', email: 'marcus@research.ai', role: 'VIEWER', status: 'inactive', last: '3d ago' },
              ].map(u => (
                <tr key={u.email}>
                  <td>
                    <div className="flex items-center gap-2.5">
                      <div className="w-7 h-7 rounded-full bg-gradient-to-br from-blue-400 to-violet-500 flex items-center justify-center text-[10px] font-bold text-white">
                        {u.name.split(' ').map(n => n[0]).join('')}
                      </div>
                      <span className="text-xs font-medium text-white/80">{u.name}</span>
                    </div>
                  </td>
                  <td className="text-xs text-white/45">{u.email}</td>
                  <td><span className="text-xs font-mono text-violet-400">{u.role}</span></td>
                  <td>
                    {u.status === 'active'
                      ? <span className="badge badge-completed">ACTIVE</span>
                      : <span className="badge badge-pending">INACTIVE</span>}
                  </td>
                  <td className="text-[11px] text-white/30">{u.last}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </motion.div>
      )}
    </div>
  )
}
