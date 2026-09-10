const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, { headers: { 'Content-Type': 'application/json' }, ...init })
  if (!response.ok) throw new Error(`API request failed: ${response.status}`)
  return response.json() as Promise<T>
}

export type ApiTask = {
  task_code: string
  department: string
  corridor_id: string
  priority_level: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | null
  priority_score: number | null
  due_at: string
  estimated_duration_minutes: number
  status: string
}

export type ApiAnalytics = {
  before: { blocks: number; downtime_minutes: number; asset_availability: number; overdue_tasks: number }
  after: { blocks: number; downtime_minutes: number; asset_availability: number; overdue_tasks: number }
  improvement: { downtime_reduced_percent: number; blocks_reduced_percent: number; availability_improvement_percent: number }
}

export const api = {
  health: () => request<{ status: string; service: string }>('/health'),
  tasks: () => request<{ items: ApiTask[]; limit: number; offset: number }>('/tasks?limit=4'),
  analytics: () => request<ApiAnalytics>('/analytics'),
  optimize: (planning_horizon: 'DAILY' | 'WEEKLY' | 'MONTHLY') => request<{ status: string; planning_horizon: string; blocks: Array<{ block_id: string; corridor_id: string; date: string; start_time: string; end_time: string; departments: string[]; shared_block: boolean; shared_block_savings_minutes: number; reason: string[] }> }>('/optimize', { method: 'POST', body: JSON.stringify({ planning_horizon }) }),
}
