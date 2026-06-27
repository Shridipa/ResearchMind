/**
 * Global Zustand store for ResearchMind 2.0 Enterprise.
 */
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export type Role = 'SUPER_ADMIN' | 'ORG_ADMIN' | 'WORKSPACE_ADMIN' | 'RESEARCHER' | 'VIEWER'

export interface AuthUser {
  id: string
  email: string
  firstName: string
  lastName: string
  role: Role
  workspaceId?: string
  organizationId?: string
}

export interface IngestionJob {
  jobId: string
  documentId: string
  documentName: string
  status: string
  progress: number
  errorMessage?: string
  workspaceId: string
}

export interface ActivityEvent {
  id: string
  action: string
  message: string
  user: string
  timestamp: string
}

export interface Notification {
  id: string
  type: 'info' | 'success' | 'warning' | 'error'
  title: string
  message: string
  timestamp: Date
  read: boolean
}

export interface RealtimeEvent {
  event_type: string
  [key: string]: any
}

interface AppState {
  user: AuthUser | null
  accessToken: string | null
  refreshToken: string | null
  setUser: (user: AuthUser | null) => void
  setAccessToken: (token: string | null) => void
  setRefreshToken: (token: string | null) => void
  startGuestSession: () => void
  logout: () => void

  ws: WebSocket | null
  wsConnected: boolean
  connectWebSocket: (workspaceId: string) => void
  disconnectWebSocket: () => void

  ingestionJobs: Record<string, IngestionJob>
  upsertJob: (job: IngestionJob) => void

  liveActivity: ActivityEvent[]
  addLiveActivity: (event: Omit<ActivityEvent, 'id'>) => void

  notifications: Notification[]
  addNotification: (n: Omit<Notification, 'id' | 'timestamp' | 'read'>) => void
  markRead: (id: string) => void
  markAllRead: () => void
  unreadCount: () => number
}

export const DEMO_WORKSPACE_ID = 'demo-workspace-001'
export const GUEST_ACCESS_TOKEN = 'researchmind-demo-guest'
export const GUEST_REFRESH_TOKEN = 'researchmind-demo-refresh'
export const GUEST_USER: AuthUser = {
  id: 'demo-user-001',
  email: 'guest@researchmind.ai',
  firstName: 'Researcher',
  lastName: 'Guest',
  role: 'WORKSPACE_ADMIN',
  workspaceId: DEMO_WORKSPACE_ID,
}

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      setUser: (user) => set({ user }),
      setAccessToken: (accessToken) => set({ accessToken }),
      setRefreshToken: (refreshToken) => set({ refreshToken }),
      startGuestSession: () => set({
        user: GUEST_USER,
        accessToken: GUEST_ACCESS_TOKEN,
        refreshToken: GUEST_REFRESH_TOKEN,
      }),
      logout: () => {
        const { ws } = get()
        if (ws) ws.close()
        set({ user: null, accessToken: null, refreshToken: null, ws: null, wsConnected: false })
      },

      ws: null,
      wsConnected: false,
      connectWebSocket: (workspaceId: string) => {
        const { ws, accessToken } = get()
        if (ws) ws.close()

        const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'
        const socket = new WebSocket(`${wsUrl}/ws/${workspaceId}?token=${accessToken ?? ''}`)

        socket.onopen = () => set({ wsConnected: true })
        socket.onclose = () => set({ wsConnected: false })

        socket.onmessage = (event) => {
          try {
            const data: RealtimeEvent = JSON.parse(event.data)
            const { upsertJob, addNotification, addLiveActivity } = get()

            if (data.event_type === 'IngestionProgressEvent') {
              upsertJob({
                jobId: data.job_id,
                documentId: data.document_id,
                documentName: data.document_name || 'Document',
                status: data.status,
                progress: data.progress,
                errorMessage: data.error_message,
                workspaceId: data.workspace_id || workspaceId,
              })
              addLiveActivity({
                action: 'INGESTION',
                message: `${data.document_name || 'Document'} → ${data.status} (${data.progress}%)`,
                user: 'System',
                timestamp: new Date().toISOString(),
              })
              if (data.status === 'COMPLETED' || data.status === 'SEARCH_READY') {
                addNotification({ type: 'success', title: 'Document Ready', message: `${data.document_name || 'Document'} is searchable.` })
              }
              if (data.status === 'FAILED') {
                addNotification({ type: 'error', title: 'Ingestion Failed', message: data.error_message || 'Processing failed' })
              }
            }

            if (data.event_type === 'ResearchProgressEvent') {
              addLiveActivity({
                action: 'RESEARCH',
                message: `Research → ${data.status} (${data.progress}%)`,
                user: 'AI Engine',
                timestamp: new Date().toISOString(),
              })
              if (data.status === 'COMPLETED') {
                addNotification({ type: 'info', title: 'Research Complete', message: `"${data.query?.slice(0, 40)}…" finished.` })
              }
            }

            if (data.event_type === 'WorkspaceActivityEvent') {
              addLiveActivity({
                action: data.action,
                message: data.message,
                user: data.user || 'System',
                timestamp: new Date().toISOString(),
              })
            }

            if (data.event_type === 'NotificationEvent') {
              addNotification({ type: data.type || 'info', title: data.title, message: data.message })
            }
          } catch { /* ignore malformed */ }
        }

        set({ ws: socket })
      },

      disconnectWebSocket: () => {
        const { ws } = get()
        if (ws) ws.close()
        set({ ws: null, wsConnected: false })
      },

      ingestionJobs: {},
      upsertJob: (job) => set(state => ({
        ingestionJobs: { ...state.ingestionJobs, [job.jobId]: job },
      })),

      liveActivity: [],
      addLiveActivity: (event) => set(state => ({
        liveActivity: [{ ...event, id: `${Date.now()}-${Math.random()}` }, ...state.liveActivity].slice(0, 50),
      })),

      notifications: [],
      addNotification: (n) => set(state => ({
        notifications: [
          { id: `${Date.now()}-${Math.random()}`, timestamp: new Date(), read: false, ...n },
          ...state.notifications,
        ].slice(0, 50),
      })),
      markRead: (id) => set(state => ({
        notifications: state.notifications.map(n => n.id === id ? { ...n, read: true } : n),
      })),
      markAllRead: () => set(state => ({
        notifications: state.notifications.map(n => ({ ...n, read: true })),
      })),
      unreadCount: () => get().notifications.filter(n => !n.read).length,
    }),
    {
      name: 'researchmind-auth',
      partialize: (s) => ({ user: s.user, accessToken: s.accessToken, refreshToken: s.refreshToken }),
    },
  ),
)
