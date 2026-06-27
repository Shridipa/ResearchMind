'use client'
import { useState } from 'react'
import {
  FolderOpen, Plus, Users, FileText, Search,
  MoreHorizontal, Clock, Zap, ChevronRight, Trash2, Settings,
} from 'lucide-react'
import { motion } from 'framer-motion'

const mockWorkspaces = [
  { id: 'ws-1', name: 'AI/ML Research', members: 8, docs: 142, activity: 'Active now', color: 'from-blue-500 to-violet-600' },
  { id: 'ws-2', name: 'NLP Papers Q3', members: 4, docs: 67, activity: '2h ago', color: 'from-violet-500 to-pink-600' },
  { id: 'ws-3', name: 'Drug Discovery', members: 12, docs: 203, activity: '1d ago', color: 'from-emerald-500 to-cyan-600' },
  { id: 'ws-4', name: 'LLM Benchmarks', members: 3, docs: 31, activity: '3d ago', color: 'from-amber-500 to-orange-600' },
]

const ROLE_COLORS: Record<string, string> = {
  WORKSPACE_ADMIN: 'text-blue-400 bg-blue-500/10 border-blue-500/25',
  RESEARCHER: 'text-violet-400 bg-violet-500/10 border-violet-500/25',
  VIEWER: 'text-white/40 bg-white/5 border-white/10',
}

const members = [
  { name: 'Jane Doe', email: 'jane@research.ai', role: 'WORKSPACE_ADMIN', avatar: 'JD' },
  { name: 'Alex Chen', email: 'alex@research.ai', role: 'RESEARCHER', avatar: 'AC' },
  { name: 'Priya Singh', email: 'priya@research.ai', role: 'RESEARCHER', avatar: 'PS' },
  { name: 'Marcus Wu', email: 'marcus@research.ai', role: 'VIEWER', avatar: 'MW' },
]

function WorkspaceCard({ ws, delay }: { ws: typeof mockWorkspaces[0], delay: number }) {
  const [menu, setMenu] = useState(false)
  return (
    <motion.div
      className="card glass-hover relative cursor-pointer"
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
    >
      <div className="flex items-start justify-between mb-4">
        <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${ws.color} flex items-center justify-center shadow-lg`}>
          <FolderOpen size={18} className="text-white" />
        </div>
        <div className="relative">
          <button
            onClick={() => setMenu(v => !v)}
            className="p-1.5 rounded-lg hover:bg-white/5 text-white/30 hover:text-white/70 transition-colors"
          >
            <MoreHorizontal size={15} />
          </button>
          {menu && (
            <div className="absolute right-0 top-8 w-40 glass rounded-xl shadow-2xl z-10 py-1.5 border border-white/10">
              <button className="w-full flex items-center gap-2.5 px-3 py-2 text-xs text-white/65 hover:bg-white/5 transition-colors">
                <Settings size={12} /> Settings
              </button>
              <button className="w-full flex items-center gap-2.5 px-3 py-2 text-xs text-rose-400 hover:bg-rose-500/5 transition-colors">
                <Trash2 size={12} /> Delete
              </button>
            </div>
          )}
        </div>
      </div>
      <h3 className="font-semibold text-white text-sm mb-1">{ws.name}</h3>
      <div className="flex items-center gap-3 text-xs text-white/40">
        <span className="flex items-center gap-1"><Users size={11} /> {ws.members} members</span>
        <span className="flex items-center gap-1"><FileText size={11} /> {ws.docs} docs</span>
      </div>
      <div className="mt-4 flex items-center justify-between">
        <span className="flex items-center gap-1.5 text-[11px] text-white/35">
          <Clock size={10} /> {ws.activity}
        </span>
        <ChevronRight size={14} className="text-white/25" />
      </div>
    </motion.div>
  )
}

export default function WorkspacePage() {
  const [showInvite, setShowInvite] = useState(false)
  const [inviteEmail, setInviteEmail] = useState('')

  return (
    <div className="space-y-6 max-w-screen-xl">
      {/* Header */}
      <div className="flex items-center justify-between animate-fade-in-up">
        <div>
          <h1 className="text-2xl font-bold text-white">Workspaces</h1>
          <p className="text-white/45 text-sm mt-1">Collaborative research spaces for your teams</p>
        </div>
        <button className="btn btn-primary">
          <Plus size={15} />
          New Workspace
        </button>
      </div>

      {/* Workspace grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        {mockWorkspaces.map((ws, i) => (
          <WorkspaceCard key={ws.id} ws={ws} delay={i * 0.07} />
        ))}
        <motion.div
          className="card glass-hover flex flex-col items-center justify-center gap-3 cursor-pointer min-h-[160px] border-dashed border-white/10"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.35 }}
        >
          <div className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center">
            <Plus size={18} className="text-white/30" />
          </div>
          <p className="text-sm text-white/35 font-medium">Create workspace</p>
        </motion.div>
      </div>

      {/* Members section */}
      <motion.div
        className="card"
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="font-semibold text-white text-sm">Team Members</h2>
            <p className="text-white/40 text-xs mt-0.5">AI/ML Research workspace</p>
          </div>
          <button onClick={() => setShowInvite(v => !v)} className="btn btn-ghost text-xs">
            <Plus size={13} /> Invite
          </button>
        </div>

        {/* Invite form */}
        {showInvite && (
          <motion.div
            className="flex gap-2 mb-4 p-3 rounded-lg bg-blue-500/5 border border-blue-500/15"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
          >
            <input
              value={inviteEmail}
              onChange={e => setInviteEmail(e.target.value)}
              placeholder="colleague@company.com"
              className="input text-xs py-2"
            />
            <button className="btn btn-primary text-xs px-4 whitespace-nowrap">Send invite</button>
          </motion.div>
        )}

        <table className="table">
          <thead>
            <tr>
              <th>Member</th>
              <th>Email</th>
              <th>Role</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {members.map(m => (
              <tr key={m.email}>
                <td>
                  <div className="flex items-center gap-2.5">
                    <div className="w-7 h-7 rounded-full bg-gradient-to-br from-blue-400 to-violet-500 flex items-center justify-center text-[10px] font-bold text-white">
                      {m.avatar}
                    </div>
                    <span className="text-white/80 font-medium text-xs">{m.name}</span>
                  </div>
                </td>
                <td className="text-white/45 text-xs">{m.email}</td>
                <td>
                  <span className={`badge border text-[10px] ${ROLE_COLORS[m.role]}`}>{m.role}</span>
                </td>
                <td>
                  <button className="btn-ghost text-xs rounded-lg px-2 py-1 text-rose-400/60 hover:text-rose-400 transition-colors">
                    Remove
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </motion.div>

      {/* Activity Feed */}
      <motion.div
        className="card"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
      >
        <h2 className="font-semibold text-white text-sm mb-4">Activity Feed</h2>
        <div className="space-y-3">
          {[
            { actor: 'Jane Doe', action: 'uploaded', target: 'GPT-4 Technical Report.pdf', time: '2m ago', icon: FileText, color: 'text-blue-400 bg-blue-500/10' },
            { actor: 'Alex Chen', action: 'ran research on', target: '"transformer attention mechanisms"', time: '15m ago', icon: Zap, color: 'text-violet-400 bg-violet-500/10' },
            { actor: 'Priya Singh', action: 'invited', target: 'Marcus Wu as VIEWER', time: '1h ago', icon: Users, color: 'text-emerald-400 bg-emerald-500/10' },
            { actor: 'Alex Chen', action: 'searched', target: '"mixture of experts scaling"', time: '2h ago', icon: Search, color: 'text-cyan-400 bg-cyan-500/10' },
          ].map((item, i) => (
            <div key={i} className="flex items-center gap-3">
              <div className={`w-8 h-8 rounded-lg ${item.color} flex items-center justify-center shrink-0`}>
                <item.icon size={13} />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs text-white/70">
                  <span className="font-semibold text-white/85">{item.actor}</span>
                  {' '}{item.action}{' '}
                  <span className="text-blue-400">{item.target}</span>
                </p>
              </div>
              <span className="text-[11px] text-white/30 whitespace-nowrap">{item.time}</span>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  )
}
