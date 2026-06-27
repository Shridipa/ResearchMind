'use client'

import { useEffect } from 'react'
import { useAppStore, DEMO_WORKSPACE_ID, GUEST_ACCESS_TOKEN, GUEST_USER } from '@/store/appStore'

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const { accessToken, user, setAccessToken, setRefreshToken, setUser, connectWebSocket } = useAppStore()

  useEffect(() => {
    if (!accessToken) {
      setUser(GUEST_USER)
      setAccessToken(GUEST_ACCESS_TOKEN)
      setRefreshToken(null)
      return
    }
    const wsId = user?.workspaceId ?? DEMO_WORKSPACE_ID
    connectWebSocket(wsId)
    return () => useAppStore.getState().disconnectWebSocket()
  }, [accessToken, user?.workspaceId, connectWebSocket, setAccessToken, setRefreshToken, setUser])

  if (!accessToken) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <p className="text-white/40 text-sm">Opening dashboard...</p>
      </div>
    )
  }

  return <>{children}</>
}

