'use client'
import { useState } from 'react'
import { Search, FileText, Star, Folder, Sliders, Clock } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { useAppStore, DEMO_WORKSPACE_ID } from '@/store/appStore'
import { search as apiSearch, startResearch, type SearchResult } from '@/lib/enterprise-api'

const recentSearches = ['transformer attention mechanisms', 'AI adoption trends', 'market analysis']

const TYPE_ICONS: Record<string, { icon: typeof FileText; color: string; bg: string }> = {
  document: { icon: FileText, color: 'text-blue-400', bg: 'bg-blue-500/10' },
  research: { icon: Star, color: 'text-violet-400', bg: 'bg-violet-500/10' },
}

function SearchResult({ result, delay }: { result: SearchResult & { snippet?: string; workspace?: string; time?: string }; delay: number }) {
  const meta = TYPE_ICONS[result.type] ?? TYPE_ICONS.document
  return (
    <motion.div
      className="card glass-hover cursor-pointer"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
    >
      <div className="flex items-start gap-3">
        <div className={`w-8 h-8 rounded-lg ${meta.bg} flex items-center justify-center shrink-0 mt-0.5`}>
          <meta.icon size={14} className={meta.color} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2">
            <h3 className="text-sm font-semibold text-white/90 truncate">{result.title}</h3>
            <div className="flex items-center gap-2 shrink-0">
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-white/5 text-white/30">{Math.round(result.score * 100)}% match</span>
              <Folder size={10} className="text-white/25" />
              <span className="text-[10px] text-white/30">{result.workspace}</span>
            </div>
          </div>
          <p className="text-xs text-white/50 mt-1.5 line-clamp-2 leading-relaxed">{result.snippet ?? result.file_name}</p>
          <div className="flex items-center gap-2 mt-2">
            <span className={`badge border text-[10px] ${meta.bg} ${meta.color} border-current/20`}>{result.type}</span>
            <span className="flex items-center gap-1 text-[10px] text-white/30">
              <Clock size={9} />{result.time}
            </span>
          </div>
        </div>
      </div>
    </motion.div>
  )
}

export default function SearchPage() {
  const { accessToken, user, addNotification } = useAppStore()
  const wsId = user?.workspaceId ?? DEMO_WORKSPACE_ID
  const [query, setQuery] = useState('')
  const [mode, setMode] = useState<'hybrid' | 'semantic' | 'keyword'>('hybrid')
  const [searching, setSearching] = useState(false)
  const [results, setResults] = useState<(SearchResult & { snippet?: string })[] | null>(null)

  const handleSearch = async () => {
    if (!query.trim() || !accessToken) return
    setSearching(true)
    try {
      const res = await apiSearch(accessToken, query, wsId)
      setResults(res.results.map(r => ({ ...r, snippet: r.file_name, workspace: 'Demo Workspace', time: new Date().toISOString().slice(0, 10) })))
    } catch {
      addNotification({ type: 'error', title: 'Search Failed', message: 'Could not reach search API.' })
    } finally {
      setSearching(false)
    }
  }

  const handleResearch = async () => {
    if (!query.trim() || !accessToken) return
    try {
      const res = await startResearch(accessToken, query, wsId)
      addNotification({ type: 'info', title: 'Research Started', message: `Job ${res.job_id} running — watch Live Activity on dashboard.` })
    } catch {
      addNotification({ type: 'error', title: 'Research Failed', message: 'Could not start research job.' })
    }
  }

  return (
    <div className="space-y-5 max-w-screen-xl">
      {/* Header */}
      <div className="animate-fade-in-up">
        <h1 className="text-2xl font-bold text-white">Enterprise Search</h1>
        <p className="text-white/45 text-sm mt-1">Hybrid semantic + keyword search across your entire research corpus</p>
      </div>

      {/* Search bar */}
      <motion.div
        className="card"
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <div className="flex gap-3">
          <div className="flex-1 relative">
            <Search size={15} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-white/30" />
            <input
              value={query}
              onChange={e => setQuery(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleSearch()}
              placeholder="Search documents, research sessions, conversations…"
              className="input text-sm"
              style={{ paddingLeft: 36 }}
            />
          </div>
          <div className="flex rounded-lg overflow-hidden border border-white/8">
            {(['hybrid', 'semantic', 'keyword'] as const).map(m => (
              <button
                key={m}
                onClick={() => setMode(m)}
                className={`px-3 py-2 text-xs font-medium transition-colors capitalize ${
                  mode === m ? 'bg-blue-500/20 text-blue-400' : 'text-white/35 hover:text-white/60 hover:bg-white/3'
                }`}
              >
                {m}
              </button>
            ))}
          </div>
          <button onClick={handleSearch} disabled={searching} className="btn btn-primary px-5">
            <Search size={14} />
            {searching ? 'Searching\u2026' : 'Search'}
          </button>
          <button onClick={handleResearch} disabled={!query.trim()} className="btn btn-ghost border border-white/10 px-4">
            Run AI Research
          </button>
        </div>

        {/* Mode description */}
        <p className="text-xs text-white/30 mt-3">
          {mode === 'hybrid' && 'Hybrid: Combines BM25 keyword matching with semantic vector similarity for best recall and precision'}
          {mode === 'semantic' && 'Semantic: Pure vector similarity \u2014 great for conceptual queries and paraphrased matches'}
          {mode === 'keyword' && 'Keyword: BM25 ranking \u2014 fastest mode, best for exact term matches'}
        </p>
      </motion.div>

      {/* Recent searches */}
      {!results && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.15 }}>
          <p className="text-xs text-white/35 mb-2 flex items-center gap-1.5">
            <Clock size={11} /> Recent searches
          </p>
          <div className="flex flex-wrap gap-2">
            {recentSearches.map(s => (
              <button key={s} onClick={() => { setQuery(s); }} className="px-3 py-1.5 rounded-full bg-white/5 border border-white/8 text-xs text-white/55 hover:bg-white/8 hover:text-white/80 transition-colors">
                {s}
              </button>
            ))}
          </div>
        </motion.div>
      )}

      {/* Results */}
      <AnimatePresence>
        {searching && (
          <div className="space-y-3">
            {[1,2,3].map(i => (
              <div key={i} className="card skeleton h-24" />
            ))}
          </div>
        )}
        {results && !searching && (
          <motion.div className="space-y-3" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <div className="flex items-center justify-between">
              <p className="text-xs text-white/40">{results.length} results for {'"'}<span className="text-white/70">{query}</span>{'"'} &middot; {mode} search</p>
              <button className="btn-ghost btn text-xs gap-1.5 py-1.5">
                <Sliders size={12} /> Filters
              </button>
            </div>
            {results.map((r, i) => (
              <SearchResult key={r.id} result={r} delay={i * 0.06} />
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}