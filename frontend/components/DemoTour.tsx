'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Upload, Search, Users, Zap, ChevronRight } from 'lucide-react'

const STEPS = [
  { title: 'Welcome to ResearchMind 2.0', desc: 'Enterprise AI research platform with distributed ingestion, real-time collaboration, and RBAC security.', icon: Zap },
  { title: 'Document Ingestion Pipeline', desc: 'Upload documents → Queue → Extract → Chunk → Embed → Index → Search-ready. Progress updates live via WebSockets.', icon: Upload },
  { title: 'AI Research Workflow', desc: 'Run asynchronous research jobs across your workspace corpus with citation-grounded results.', icon: Search },
  { title: 'Team Collaboration', desc: 'Multi-user workspaces, role-based permissions, activity feeds, and document version history.', icon: Users },
]

export function DemoTour({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [step, setStep] = useState(0)
  const current = STEPS[step]
  const Icon = current.icon

  if (!open) return null

  return (
    <AnimatePresence>
      <div className="command-overlay" onClick={onClose}>
        <motion.div
          className="command-box max-w-lg"
          initial={{ opacity: 0, scale: 0.94 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.94 }}
          onClick={e => e.stopPropagation()}
        >
          <div className="flex items-center justify-between px-5 py-4 border-b border-white/8">
            <span className="text-xs font-semibold tracking-widest text-white/40 uppercase">Interactive Demo</span>
            <button onClick={onClose} className="text-white/40 hover:text-white/70"><X size={16} /></button>
          </div>
          <div className="p-6">
            <div className="w-12 h-12 rounded-xl bg-blue-500/20 flex items-center justify-center mb-4">
              <Icon size={22} className="text-blue-400" />
            </div>
            <h3 className="text-lg font-bold text-white mb-2">{current.title}</h3>
            <p className="text-sm text-white/55 leading-relaxed">{current.desc}</p>
            <div className="flex gap-1.5 mt-6">
              {STEPS.map((_, i) => (
                <div key={i} className={`h-1 flex-1 rounded-full ${i <= step ? 'bg-blue-500' : 'bg-white/10'}`} />
              ))}
            </div>
          </div>
          <div className="flex justify-between px-5 py-4 border-t border-white/8">
            <button onClick={onClose} className="btn btn-ghost text-xs">Skip</button>
            {step < STEPS.length - 1 ? (
              <button onClick={() => setStep(s => s + 1)} className="btn btn-primary text-xs gap-1">
                Next <ChevronRight size={14} />
              </button>
            ) : (
              <button onClick={onClose} className="btn btn-primary text-xs">Got it</button>
            )}
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  )
}
