'use client'

import { useEffect } from 'react'
import { useAppStore, DEMO_WORKSPACE_ID } from '@/store/appStore'

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const { accessToken, user, startGuestSession, connectWebSocket } = useAppStore()

  useEffect(() => {
    if (!accessToken) {
      startGuestSession()
      return
    }
    const wsId = user?.workspaceId ?? DEMO_WORKSPACE_ID
    connectWebSocket(wsId)
    return () => useAppStore.getState().disconnectWebSocket()
  }, [accessToken, user?.workspaceId, connectWebSocket, startGuestSession])

  if (!accessToken) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <p className="text-white/40 text-sm">Opening dashboard...</p>
      </div>
    )
  }

  return <>{children}</>
}

