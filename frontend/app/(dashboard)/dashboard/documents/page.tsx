'use client'
import { useState, useEffect, useCallback, useRef } from 'react'
import {
  Upload, FileText, RefreshCw, Eye, Trash2, Filter,
  GitCommit, RotateCcw,
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { useAppStore, DEMO_WORKSPACE_ID } from '@/store/appStore'
import { getDocuments, uploadDocument, deleteDocument, type DocumentItem } from '@/lib/enterprise-api'

const STATUS_CLASS: Record<string, string> = {
  COMPLETED: 'badge-completed',
  EMBEDDING: 'badge-processing',
  CHUNKING: 'badge-processing',
  PROCESSING: 'badge-processing',
  INDEXING: 'badge-processing',
  PENDING: 'badge-pending',
  FAILED: 'badge-failed',
}


function DropZone({ onDrop, uploading }: { onDrop: (files: File[]) => void; uploading: boolean }) {
  const [dragging, setDragging] = useState(false)
  const ref = useRef<HTMLInputElement>(null)

  return (
    <div
      className={`relative border-2 border-dashed rounded-xl p-8 flex flex-col items-center gap-3 transition-all cursor-pointer
        ${dragging ? 'border-blue-400 bg-blue-500/5' : 'border-white/10 hover:border-white/20 hover:bg-white/2'}`}
      onDragOver={e => { e.preventDefault(); setDragging(true) }}
      onDragLeave={() => setDragging(false)}
      onDrop={e => { e.preventDefault(); setDragging(false); onDrop(Array.from(e.dataTransfer.files)) }}
      onClick={() => !uploading && ref.current?.click()}
    >
      <input ref={ref} type="file" multiple accept=".pdf,.docx,.txt,.md" className="hidden" disabled={uploading}
        onChange={e => onDrop(Array.from(e.target.files || []))} />
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center transition-colors ${dragging ? 'bg-blue-500/20' : 'bg-white/5'}`}>
        <Upload size={20} className={dragging ? 'text-blue-400' : 'text-white/30'} />
      </div>
      <div className="text-center">
        <p className="text-sm font-medium text-white/70">Drop PDFs, DOCX, or TXT files here</p>
        <p className="text-xs text-white/30 mt-1">or click to browse · Max 50MB per file</p>
      </div>
    </div>
  )
}

export default function DocumentsPage() {
  const { accessToken, user, ingestionJobs, addNotification } = useAppStore()
  const wsId = user?.workspaceId ?? DEMO_WORKSPACE_ID
  const [selectedDoc, setSelectedDoc] = useState<string | null>(null)
  const [showVersions, setShowVersions] = useState(false)
  const [filter, setFilter] = useState('ALL')
  const [docs, setDocs] = useState<DocumentItem[]>([])
  const [uploading, setUploading] = useState(false)

  const loadDocs = useCallback(async () => {
    if (!accessToken) return
    try {
      const res = await getDocuments(accessToken, wsId)
      setDocs(res.documents.map(d => {
        const live = ingestionJobs[Object.values(ingestionJobs).find(j => j.documentId === d.id)?.jobId ?? '']
        return live ? { ...d, status: live.status, progress: live.progress } : d
      }))
    } catch { /* ignore */ }
  }, [accessToken, wsId, ingestionJobs])

  useEffect(() => { loadDocs() }, [loadDocs])
  useEffect(() => {
    const t = setInterval(loadDocs, 5000)
    return () => clearInterval(t)
  }, [loadDocs])

  const handleDrop = async (files: File[]) => {
    if (!accessToken) return
    setUploading(true)
    for (const file of files) {
      try {
        await uploadDocument(accessToken, wsId, file)
        addNotification({ type: 'success', title: 'Upload Queued', message: `${file.name} is being processed.` })
      } catch {
        addNotification({ type: 'error', title: 'Upload Failed', message: file.name })
      }
    }
    setUploading(false)
    loadDocs()
  }

  const handleDelete = async (docId: string) => {
    if (!accessToken || !confirm('Delete this document?')) return
    await deleteDocument(accessToken, wsId, docId)
    loadDocs()
  }

  const filtered = filter === 'ALL' ? docs : docs.filter(d => d.status === filter)
  const selected = docs.find(d => d.id === selectedDoc)
  const versionHistory = selected?.versions?.map(v => ({
    version: v.version,
    date: new Date(v.created_at).toLocaleString(),
    author: v.author,
    summary: v.summary,
  })) ?? []

  return (
    <div className="space-y-5 max-w-screen-xl">
      {/* Header */}
      <div className="flex items-center justify-between animate-fade-in-up">
        <div>
          <h1 className="text-2xl font-bold text-white">Document Library</h1>
          <p className="text-white/45 text-sm mt-1">Manage, version, and monitor document ingestion</p>
        </div>
        <div className="flex gap-2">
          <div className="relative">
            <select
              value={filter}
              onChange={e => setFilter(e.target.value)}
              className="input text-xs pr-8 appearance-none"
              style={{ paddingLeft: 32 }}
            >
              <option value="ALL">All statuses</option>
              <option value="COMPLETED">Completed</option>
              <option value="PROCESSING">Processing</option>
              <option value="PENDING">Pending</option>
              <option value="FAILED">Failed</option>
            </select>
            <Filter size={12} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-white/35 pointer-events-none" />
          </div>
        </div>
      </div>

      {/* Drop zone */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 }}>
        <DropZone onDrop={handleDrop} uploading={uploading} />
      </motion.div>

      {uploading && (
        <div className="card card-sm text-xs text-white/50 flex items-center gap-2">
          <RefreshCw size={14} className="animate-spin text-blue-400" /> Uploading and starting ingestion pipeline…
        </div>
      )}

      {/* Table */}
      <div className="flex gap-4">
        <motion.div className="card flex-1 overflow-hidden" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <table className="table">
            <thead>
              <tr>
                <th>Document</th>
                <th>Uploaded By</th>
                <th>Status</th>
                <th>Versions</th>
                <th>Time</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(doc => (
                <tr key={doc.id} className={`cursor-pointer ${selectedDoc === doc.id ? 'bg-blue-500/5' : ''}`}
                  onClick={() => setSelectedDoc(doc.id === selectedDoc ? null : doc.id)}>
                  <td>
                    <div className="flex items-center gap-2.5">
                      <div className="w-7 h-7 rounded-lg bg-blue-500/10 flex items-center justify-center">
                        <FileText size={13} className="text-blue-400" />
                      </div>
                      <div>
                        <p className="text-xs font-medium text-white/85 truncate max-w-[200px]">{doc.title}</p>
                        <p className="text-[10px] text-white/35">{doc.file_type} · {doc.file_name}</p>
                      </div>
                    </div>
                  </td>
                  <td className="text-xs text-white/50">{doc.uploaded_by}</td>
                  <td>
                    <div className="space-y-1">
                      <span className={`badge ${STATUS_CLASS[doc.status]}`}>{doc.status}</span>
                      {doc.progress > 0 && doc.status !== 'COMPLETED' && doc.status !== 'FAILED' && (
                        <div className="progress-bar w-16">
                          <div className="progress-fill" style={{ width: `${doc.progress}%` }} />
                        </div>
                      )}
                    </div>
                  </td>
                  <td>
                    <button
                      className="flex items-center gap-1 text-xs text-white/45 hover:text-blue-400 transition-colors"
                      onClick={e => { e.stopPropagation(); setSelectedDoc(doc.id); setShowVersions(true) }}
                    >
                      <GitCommit size={11} />
                      v{doc.versions?.length ?? 1}
                    </button>
                  </td>
                  <td className="text-xs text-white/35">{new Date(doc.uploaded_at).toLocaleDateString()}</td>
                  <td>
                    <div className="flex items-center gap-1">
                      {doc.status === 'FAILED' && (
                        <button className="p-1.5 rounded-lg hover:bg-orange-500/10 text-orange-400/60 hover:text-orange-400 transition-colors">
                          <RefreshCw size={12} />
                        </button>
                      )}
                      <button className="p-1.5 rounded-lg hover:bg-white/5 text-white/25 hover:text-white/60 transition-colors">
                        <Eye size={12} />
                      </button>
                      <button onClick={e => { e.stopPropagation(); handleDelete(doc.id) }} className="p-1.5 rounded-lg hover:bg-rose-500/5 text-rose-400/30 hover:text-rose-400 transition-colors">
                        <Trash2 size={12} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </motion.div>

        {/* Version History Panel */}
        <AnimatePresence>
          {selectedDoc && showVersions && (
            <motion.div
              className="card w-72 shrink-0"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-semibold text-white">Version History</h3>
                <button onClick={() => setShowVersions(false)} className="text-white/30 hover:text-white/60 transition-colors text-xs">
                  Close
                </button>
              </div>
              <p className="text-xs text-white/45 mb-4 truncate">{selected?.title}</p>
              <div className="space-y-3">
                {versionHistory.map(v => (
                  <div key={v.version} className="relative pl-5">
                    <div className="absolute left-0 top-1 w-3 h-3 rounded-full border-2 border-blue-400 bg-[rgb(9,9,11)]" />
                    {v.version !== 1 && <div className="absolute left-1.5 top-4 bottom-0 w-px bg-white/8" />}
                    <div className="space-y-0.5">
                      <div className="flex items-center gap-2">
                        <span className="text-[11px] font-semibold text-blue-400">v{v.version}</span>
                        <span className="text-[10px] text-white/30">{v.date}</span>
                      </div>
                      <p className="text-xs text-white/60">{v.summary}</p>
                      <p className="text-[10px] text-white/30">by {v.author}</p>
                      {v.version !== versionHistory[0].version && (
                        <button className="flex items-center gap-1 text-[10px] text-orange-400/60 hover:text-orange-400 transition-colors mt-1">
                          <RotateCcw size={9} /> Rollback to v{v.version}
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
