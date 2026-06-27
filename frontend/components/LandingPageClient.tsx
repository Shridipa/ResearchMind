'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import {
  Zap, Shield, BarChart3, Users, GitBranch, Layers, Radio,
  Lock, Activity, Server, ArrowRight, CheckCircle,
} from 'lucide-react'
import { useAppStore, GUEST_ACCESS_TOKEN, GUEST_REFRESH_TOKEN, GUEST_USER } from '@/store/appStore'

const FEATURES = [
  { name: 'Hybrid Retrieval', desc: 'Dense semantic search combined with sparse BM25 for maximum recall.' },
  { name: 'Citation Grounding', desc: 'Every answer is anchored to specific page-level evidence from your papers.' },
  { name: 'Local-First RAG', desc: 'High-confidence queries are answered locally without any API call.' },
  { name: 'Multi-Paper Analysis', desc: 'Cross-document semantic comparison powered by paper comparator engine.' },
  { name: 'Research Memory', desc: 'Sessions persist conversation history with grounding scores across turns.' },
  { name: 'Evaluation Dashboard', desc: 'RAGAS-powered faithfulness and relevancy scoring for every run.' },
  { name: 'Benchmarking', desc: 'Live hallucination rate, latency trends, and embedding model comparisons.' },
  { name: 'Literature Review', desc: 'Generate structured literature reviews grounded in your uploaded corpus.' },
]

const ENTERPRISE_FEATURES = [
  { icon: Layers, title: 'Distributed Document Processing', desc: 'Celery worker pools handle upload → chunk → embed → index asynchronously.' },
  { icon: Radio, title: 'Event-Driven Architecture', desc: 'Redis pub/sub domain events decouple services for scalable processing.' },
  { icon: Users, title: 'Real-Time Collaboration', desc: 'WebSocket-driven updates for team activity, ingestion, and research.' },
  { icon: GitBranch, title: 'Document Versioning', desc: 'Full version history, comparison, and rollback for every artifact.' },
  { icon: Shield, title: 'Multi-Workspace Support', desc: 'Organizations → workspaces → documents with tenant isolation.' },
  { icon: Lock, title: 'Enterprise RBAC Security', desc: 'JWT auth with 5-level role hierarchy and permission guards.' },
  { icon: Zap, title: 'Redis-Powered Live Updates', desc: 'Real-time progress, notifications, and activity feeds.' },
  { icon: BarChart3, title: 'Monitoring & Analytics', desc: 'Prometheus metrics, queue depth, and processing throughput.' },
  { icon: Activity, title: 'Asynchronous AI Research Jobs', desc: 'Background research sessions with live stage tracking.' },
  { icon: Server, title: 'Production-Ready Infrastructure', desc: 'Docker Compose, Kubernetes manifests, and CI/CD pipeline.' },
]

const HOW_IT_WORKS = [
  {
    step: '01',
    title: 'Upload Papers',
    points: [
      'PDF ingestion via PyMuPDF',
      'Adaptive chunking with overlap',
      'Metadata extraction (abstract, methodology, limitations)',
      'FAISS vector indexing + BM25 sparse index',
    ],
  },
  {
    step: '02',
    title: 'Research Intelligence',
    points: [
      'Hybrid dense + sparse retrieval',
      'Cross-encoder re-ranking',
      'Citation-aware grounded answers',
      'Hallucination detection via evidence matcher',
    ],
  },
  {
    step: '03',
    title: 'Evaluation & Benchmarking',
    points: [
      'RAGAS faithfulness + relevancy scoring',
      'Real-time confidence heatmaps',
      'Experiment history persisted locally',
      'Embedding model comparison dashboard',
    ],
  },
]

const HERO_BADGES = [
  { icon: Zap, label: 'Event-Driven Architecture' },
  { icon: Server, label: 'Distributed AI Processing' },
  { icon: Lock, label: 'Enterprise Security' },
  { icon: BarChart3, label: 'Real-Time Analytics' },
  { icon: Users, label: 'Multi-Workspace Collaboration' },
]

const HERO_STATS = [
  { value: '10,000+', label: 'Documents Processed' },
  { value: '1,000+', label: 'Research Sessions' },
  { value: '99.9%', label: 'Processing Reliability' },
  { value: '<1s', label: 'Search Response' },
  { value: 'Live', label: 'Team Collaboration' },
]

const PIPELINE = ['Upload', 'Queue', 'AI Processing', 'Vector Index', 'Search', 'Insights']

export default function LandingPageClient() {
  const router = useRouter()
  const { setUser, setAccessToken, setRefreshToken, addNotification } = useAppStore()
  const [loading, setLoading] = useState(false)

  const openDashboard = () => {
    setLoading(true)
    setUser(GUEST_USER)
    setAccessToken(GUEST_ACCESS_TOKEN)
    setRefreshToken(GUEST_REFRESH_TOKEN)
    addNotification({ type: 'success', title: 'Dashboard Opened', message: 'Guest workspace loaded instantly. No sign in required.' })
    router.push('/dashboard')
  }

  return (
    <div className="min-h-screen bg-[rgb(9,9,11)] text-white/87">
      {/* Navbar */}
      <header className="sticky top-0 z-50 border-b border-white/5 bg-[rgb(9,9,11)]/90 backdrop-blur-xl">
        <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-6">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-blue-500 to-violet-600 flex items-center justify-center">
              <Zap size={14} className="text-white" />
            </div>
            <div>
              <span className="text-sm font-bold gradient-text-blue">ResearchMind</span>
              <span className="block text-[9px] text-white/30 tracking-widest -mt-0.5">ENTERPRISE 2.0</span>
            </div>
          </div>
          <nav className="flex items-center gap-2">
            <button onClick={openDashboard} disabled={loading} className="btn btn-primary text-xs">
              {loading ? 'Opening...' : 'Open Dashboard'}
            </button>
          </nav>
        </div>
      </header>

      {/* Hero — original content preserved */}
      <section className="mx-auto max-w-6xl px-6 pb-16 pt-16 text-center">
        <div className="flex flex-wrap justify-center gap-2 mb-6">
          {HERO_BADGES.map(b => (
            <span key={b.label} className="inline-flex items-center gap-1.5 rounded-full border border-white/10 bg-white/4 px-3 py-1 text-[11px] font-medium text-white/60">
              <b.icon size={11} className="text-blue-400" /> {b.label}
            </span>
          ))}
        </div>

        <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-3 py-1 text-xs font-medium text-emerald-400">
          Local-first · Evidence-grounded · Research-grade
        </div>
        <h1 className="mx-auto max-w-3xl text-4xl md:text-5xl font-bold leading-[1.15] tracking-tight text-white">
          Grounded AI Research Workspace
        </h1>
        <p className="mx-auto mt-5 max-w-xl text-base leading-relaxed text-white/50">
          Upload papers, build semantic indexes, retrieve evidence-backed answers, compare research, and evaluate
          retrieval quality — all running locally first.
        </p>

        <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
          <button onClick={openDashboard} disabled={loading} className="btn btn-primary px-6 py-2.5 text-sm">
            Open Dashboard <ArrowRight size={15} />
          </button>
        </div>

        <div className="mt-10 flex flex-wrap items-center justify-center gap-2 text-xs text-white/35">
          {['Upload', 'Process', 'Search', 'Analyze', 'Ready'].map((step, i, arr) => (
            <span key={step} className="flex items-center gap-2">
              <span className="font-medium text-white/50">{step}</span>
              {i < arr.length - 1 && <span className="text-white/20">→</span>}
            </span>
          ))}
        </div>

        {/* Hero stats */}
        <div className="mt-14 grid grid-cols-2 md:grid-cols-5 gap-3">
          {HERO_STATS.map((s, i) => (
            <motion.div
              key={s.label}
              className="glass glass-hover rounded-xl p-4 text-center"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.08 }}
            >
              <p className="text-xl md:text-2xl font-bold gradient-text-blue">{s.value}</p>
              <p className="text-[11px] text-white/40 mt-1">{s.label}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* How It Works — original content */}
      <section className="border-y border-white/5 bg-white/[0.02] py-16">
        <div className="mx-auto max-w-6xl px-6">
          <h2 className="mb-10 text-center text-sm font-bold uppercase tracking-widest text-white/30">How It Works</h2>
          <div className="grid gap-6 md:grid-cols-3">
            {HOW_IT_WORKS.map(col => (
              <div key={col.step} className="glass glass-hover rounded-xl p-6">
                <div className="mb-3 text-xs font-bold text-emerald-400">{col.step}</div>
                <h3 className="mb-4 text-base font-semibold text-white">{col.title}</h3>
                <ul className="space-y-2">
                  {col.points.map(point => (
                    <li key={point} className="flex items-start gap-2 text-sm text-white/50">
                      <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-emerald-400" />
                      {point}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Platform Features — original content */}
      <section className="mx-auto max-w-6xl px-6 py-16">
        <h2 className="mb-10 text-center text-sm font-bold uppercase tracking-widest text-white/30">Platform Features</h2>
        <div className="grid gap-x-12 gap-y-6 sm:grid-cols-2">
          {FEATURES.map(feat => (
            <div key={feat.name} className="flex items-start gap-3 border-b border-white/5 pb-6">
              <span className="mt-0.5 h-2 w-2 shrink-0 rounded-full bg-emerald-400" />
              <div>
                <div className="text-sm font-semibold text-white/85">{feat.name}</div>
                <div className="mt-0.5 text-sm text-white/45">{feat.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* NEW: Enterprise Features */}
      <section className="border-t border-white/5 bg-white/[0.02] py-16">
        <div className="mx-auto max-w-6xl px-6">
          <h2 className="mb-3 text-center text-sm font-bold uppercase tracking-widest text-white/30">Enterprise 2.0</h2>
          <p className="text-center text-white/45 text-sm mb-10 max-w-lg mx-auto">Production-grade architecture for teams processing thousands of research artifacts.</p>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {ENTERPRISE_FEATURES.map((f, i) => (
              <motion.div
                key={f.title}
                className="glass glass-hover rounded-xl p-5"
                initial={{ opacity: 0, y: 10 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.04 }}
              >
                <f.icon size={18} className="text-blue-400 mb-3" />
                <h3 className="text-sm font-semibold text-white mb-1">{f.title}</h3>
                <p className="text-xs text-white/45 leading-relaxed">{f.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* NEW: Architecture Pipeline */}
      <section className="py-16">
        <div className="mx-auto max-w-6xl px-6 text-center">
          <h2 className="text-sm font-bold uppercase tracking-widest text-white/30 mb-10">Enterprise Architecture</h2>
          <div className="flex flex-wrap items-center justify-center gap-2 md:gap-0">
            {PIPELINE.map((step, i) => (
              <div key={step} className="flex items-center">
                <div className="glass rounded-lg px-4 py-3 min-w-[100px]">
                  <CheckCircle size={14} className="text-emerald-400 mx-auto mb-1" />
                  <p className="text-xs font-medium text-white/70">{step}</p>
                </div>
                {i < PIPELINE.length - 1 && <div className="hidden md:block w-8 h-px bg-gradient-to-r from-blue-500/50 to-violet-500/50 mx-1" />}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* NEW: Collaboration + Monitoring */}
      <section className="border-t border-white/5 py-16">
        <div className="mx-auto max-w-6xl px-6 grid md:grid-cols-2 gap-8">
          <div className="glass rounded-xl p-6">
            <Users size={20} className="text-violet-400 mb-4" />
            <h3 className="text-lg font-bold text-white mb-3">Team Collaboration</h3>
            <ul className="space-y-2 text-sm text-white/50">
              {['Multi-user workspaces', 'Role-based permissions', 'Activity feeds', 'Shared research collections', 'Document version history'].map(item => (
                <li key={item} className="flex items-center gap-2"><CheckCircle size={13} className="text-emerald-400" />{item}</li>
              ))}
            </ul>
          </div>
          <div className="glass rounded-xl p-6">
            <BarChart3 size={20} className="text-cyan-400 mb-4" />
            <h3 className="text-lg font-bold text-white mb-3">Monitoring & Observability</h3>
            <ul className="space-y-2 text-sm text-white/50">
              {['Real-time monitoring', 'Queue analytics', 'Worker health', 'Processing metrics', 'Prometheus + Grafana'].map(item => (
                <li key={item} className="flex items-center gap-2"><CheckCircle size={13} className="text-emerald-400" />{item}</li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      {/* CTA — original content */}
      <section className="mx-auto max-w-6xl px-6 pb-16">
        <div className="glass rounded-xl p-8 text-center border border-emerald-500/15">
          <h3 className="text-lg font-semibold text-white">Ready to start your research session?</h3>
          <p className="mt-2 text-sm text-white/50">
            Upload your first paper and query it with full citation grounding in under a minute.
          </p>
          <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
            <button onClick={openDashboard} disabled={loading} className="btn btn-primary">
              Open Dashboard <ArrowRight size={15} />
            </button>
          <button onClick={openDashboard} disabled={loading} className="btn btn-ghost border border-white/10">
              Continue as Guest
            </button>
          </div>
          <p className="mt-4 text-[11px] text-white/30">No sign in required</p>
        </div>
      </section>

      <footer className="border-t border-white/5 py-6 text-center text-xs text-white/30">
        ResearchMind AI — Local-first research intelligence platform · Enterprise 2.0
      </footer>

    </div>
  )
}
