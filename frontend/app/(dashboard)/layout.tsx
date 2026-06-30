'use client'
import React, { useState, useCallback } from 'react'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import {
  LayoutDashboard, FolderOpen, Search, FlaskConical,
  Shield, Bell, ChevronDown, LogOut,
  Zap, Activity, Command, BarChart3, X,
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { AuthProvider } from '@/components/AuthProvider'
import { useAppStore } from '@/store/appStore'
import { logout as apiLogout } from '@/lib/enterprise-api'

const navItems = [
  { href: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { href: '/dashboard/workspace', icon: FolderOpen, label: 'Workspaces' },
  { href: '/dashboard/documents', icon: FlaskConical, label: 'Documents' },
  { href: '/dashboard/search', icon: Search, label: 'Search' },
  { href: '/dashboard/analytics', icon: BarChart3, label: 'Analytics' },
  { href: '/dashboard/admin', icon: Shield, label: 'Admin' },
]

function CommandPalette({ onClose }: { onClose: () => void }) {
  const [query, setQuery] = useState('')
  const items = [
    { label: 'Go to Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { label: 'Upload Document', href: '/dashboard/documents', icon: FlaskConical },
    { label: 'Search Research', href: '/dashboard/search', icon: Search },
    { label: 'Admin Portal', href: '/dashboard/admin', icon: Shield },
  ].filter(i => i.label.toLowerCase().includes(query.toLowerCase()))

  return (
    <div className="command-overlay" onClick={onClose}>
      <motion.div
        className="command-box"
        initial={{ opacity: 0, scale: 0.94, y: -12 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.94, y: -12 }}
        transition={{ duration: 0.18 }}
        onClick={e => e.stopPropagation()}
      >
        <div className="flex items-center gap-3 px-4 py-3 border-b border-white/8">
          <Search size={15} className="text-white/40" />
          <input
            autoFocus
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder="Search commands, pages, documents\u2026"
            className="flex-1 bg-transparent border-0 outline-none text-sm text-white/80 placeholder-white/30"
          />
          <kbd className="text-white/30 text-xs px-1.5 py-0.5 rounded bg-white/5 border border-white/10">ESC</kbd>
        </div>
        <div className="py-2 max-h-72 overflow-y-auto">
          {items.length === 0 ? (
            <p className="text-center text-white/30 text-sm py-8">No results for {'\u201C'}{query}{'\u201D'}</p>
          ) : items.map(item => (
            <Link key={item.href} href={item.href} onClick={onClose}>
              <div className="flex items-center gap-3 px-4 py-3 hover:bg-white/5 cursor-pointer transition-colors">
                <item.icon size={15} className="text-blue-400" />
                <span className="text-sm text-white/75">{item.label}</span>
              </div>
            </Link>
          ))}
        </div>
      </motion.div>
    </div>
  )
}

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const router = useRouter()
  const [cmdOpen, setCmdOpen] = useState(false)
  const { user, accessToken, logout, notifications, unreadCount, wsConnected } = useAppStore()

  const handleLogout = async () => {
    try {
      if (accessToken) await apiLogout(accessToken)
    } catch { /* ignore */ }
    logout()
    router.push('/')
  }

  const initials = user ? `${user.firstName?.[0] ?? ''}${user.lastName?.[0] ?? ''}`.toUpperCase() || 'RM' : 'RM'

  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault()
      setCmdOpen(v => !v)
    }
    if (e.key === 'Escape') setCmdOpen(false)
  }, [])

  React.useEffect(() => {
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [handleKeyDown])

  return (
    <AuthProvider>
    <div className="flex min-h-screen">
      {/* ── Sidebar ── */}
      <aside className="sidebar">
        {/* Logo */}
        <div className="flex items-center gap-2.5 px-5 py-5 border-b border-white/5">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-blue-500 to-violet-600 flex items-center justify-center shadow-lg">
            <Zap size={14} className="text-white" />
          </div>
          <div>
            <span className="font-bold text-sm gradient-text-blue">ResearchMind</span>
            <span className="block text-[10px] text-white/30 -mt-0.5 font-medium tracking-widest">ENTERPRISE 2.0</span>
          </div>
        </div>

        {/* Command palette trigger */}
        <div className="px-4 pt-4 pb-2">
          <button
            onClick={() => setCmdOpen(true)}
            className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg bg-white/4 border border-white/6 text-white/35 text-xs hover:bg-white/6 transition-colors"
          >
            <Command size={12} />
            <span>Quick search\u2026</span>
            <span className="ml-auto opacity-60">⌘K</span>
          </button>
        </div>

        {/* Nav */}
        <nav className="flex-1 pt-2 pb-4 overflow-y-auto">
          <p className="px-5 py-2 text-[10px] font-semibold tracking-widest text-white/25 uppercase">Platform</p>
          {navItems.map(item => {
            const active = pathname === item.href || (item.href !== '/dashboard' && pathname.startsWith(item.href))
            return (
              <Link key={item.href} href={item.href} className={`sidebar-item ${active ? 'active' : ''}`}>
                <item.icon size={15} />
                {item.label}
                {item.label === 'Admin' && (
                  <span className="ml-auto text-[10px] px-1.5 py-0.5 rounded-full bg-violet-500/20 text-violet-400 border border-violet-500/25">Pro</span>
                )}
              </Link>
            )
          })}
        </nav>

        {/* User */}
        <div className="p-4 border-t border-white/5">
          <div className="flex items-center gap-3 px-2 py-2.5 rounded-lg hover:bg-white/5 cursor-pointer transition-colors group" onClick={handleLogout}>
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-400 to-violet-500 flex items-center justify-center text-xs font-bold text-white shrink-0">{initials}</div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-semibold text-white/80 truncate">{user ? `${user.firstName} ${user.lastName}` : 'Guest'}</p>
              <p className="text-[10px] text-white/35 truncate">{user?.email ?? ''}</p>
            </div>
            <LogOut size={13} className="text-white/25 group-hover:text-white/50 transition-colors" />
          </div>
        </div>
      </aside>

      {/* ── Main ── */}
      <div className="flex-1 ml-[260px] flex flex-col min-h-screen">
        {/* Top bar */}
        <header className="sticky top-0 z-30 h-14 flex items-center justify-between px-6 border-b border-white/5 bg-[rgb(9,9,11)]/80 backdrop-blur-xl">
          <div className="flex items-center gap-2 text-white/40 text-sm">
            <Activity size={14} className={wsConnected ? 'text-emerald-400' : 'text-amber-400'} />
            <span className="text-white/55">{wsConnected ? 'Live' : 'Connecting\u2026'}</span>
          </div>
          <div className="flex items-center gap-3">
            <button className="relative p-2 rounded-lg hover:bg-white/5 text-white/50 hover:text-white/80 transition-colors">
              <Bell size={16} />
              {unreadCount() > 0 && <span className="notification-dot" />}
            </button>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 p-6">
          <AnimatePresence mode="wait">
            <motion.div
              key={pathname}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.2 }}
            >
              {children}
            </motion.div>
          </AnimatePresence>
        </main>
      </div>

      {/* Command Palette */}
      <AnimatePresence>
        {cmdOpen && <CommandPalette onClose={() => setCmdOpen(false)} />}
      </AnimatePresence>
    </div>
    </AuthProvider>
  )
}