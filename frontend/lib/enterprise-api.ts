const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000'

export type AuthUser = {
  id: string
  email: string
  firstName: string
  lastName: string
  role: string
  workspaceId: string
}

export type TokenResponse = {
  access_token: string
  refresh_token: string
  token_type: string
  user?: AuthUser
}

async function apiFetch<T>(path: string, options: RequestInit = {}, token?: string | null): Promise<T> {
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string> ?? {}),
  }
  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = headers['Content-Type'] ?? 'application/json'
  }
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(`${API_BASE}/api/v1${path}`, { ...options, headers })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || res.statusText)
  }
  return res.json()
}

export async function demoLogin(): Promise<TokenResponse> {
  return apiFetch<TokenResponse>('/auth/demo-login', { method: 'POST' })
}

export async function login(email: string, password: string): Promise<TokenResponse> {
  const body = new URLSearchParams({ username: email, password })
  const res = await fetch(`${API_BASE}/api/v1/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body,
  })
  if (!res.ok) throw new Error('Login failed')
  return res.json()
}

export async function logout(token: string): Promise<void> {
  await apiFetch('/auth/logout', { method: 'POST' }, token)
}

export async function getDashboardMetrics(token: string) {
  return apiFetch<Record<string, unknown>>('/dashboard/metrics', {}, token)
}

export async function getDashboardActivity(token: string) {
  return apiFetch<{ chart: Array<{ time: string; docs: number; research: number }>; recent: ActivityItem[] }>(
    '/dashboard/activity', {}, token
  )
}

export async function getDashboardJobs(token: string) {
  return apiFetch<{ jobs: IngestionJob[]; total: number }>('/dashboard/jobs', {}, token)
}

export async function getSystemActivity(token: string) {
  return apiFetch<{ events: ActivityItem[] }>('/dashboard/system-activity', {}, token)
}

export async function getWorkspace(token: string, workspaceId: string) {
  return apiFetch(`/workspaces/${workspaceId}`, {}, token)
}

export async function getDocuments(token: string, workspaceId: string) {
  return apiFetch<{ documents: DocumentItem[]; total: number }>(`/workspaces/${workspaceId}/documents`, {}, token)
}

export async function uploadDocument(token: string, workspaceId: string, file: File) {
  const form = new FormData()
  form.append('file', file)
  return apiFetch<{ job_id: string; document_id: string; file_name: string }>(
    `/workspaces/${workspaceId}/documents`,
    { method: 'POST', body: form },
    token,
  )
}

export async function deleteDocument(token: string, workspaceId: string, documentId: string) {
  return apiFetch(`/workspaces/${workspaceId}/documents/${documentId}`, { method: 'DELETE' }, token)
}

export async function retryJob(token: string, jobId: string) {
  return apiFetch(`/ingestion-jobs/${jobId}/retry`, { method: 'POST' }, token)
}

export async function search(token: string, query: string, workspaceId: string) {
  return apiFetch<{ results: SearchResult[]; total: number }>(
    '/search',
    { method: 'POST', body: JSON.stringify({ query, workspace_id: workspaceId, mode: 'hybrid' }) },
    token,
  )
}

export async function startResearch(token: string, query: string, workspaceId: string) {
  return apiFetch<{ job_id: string; status: string }>(
    '/research/start',
    { method: 'POST', body: JSON.stringify({ query, workspace_id: workspaceId }) },
    token,
  )
}

export type ActivityItem = {
  id: string
  action: string
  message: string
  user: string
  timestamp: string
}

export type IngestionJob = {
  id: string
  document_id: string
  workspace_id: string
  document_name: string
  status: string
  progress: number
  error_message?: string | null
  created_at?: string
}

export type DocumentItem = {
  id: string
  title: string
  file_name: string
  file_type: string
  status: string
  progress: number
  uploaded_by: string
  uploaded_at: string
  versions?: Array<{ version: number; created_at: string; author: string; summary: string }>
}

export type SearchResult = {
  id: string
  title: string
  file_name: string
  score: number
  type: string
}
