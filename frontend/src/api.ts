import type {
  ConnectorInfo,
  CronJob,
  Listing,
  ListingsPage,
  RunRecord,
  RunStarted,
} from './types'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!res.ok) {
    const body = await res.text()
    throw new Error(`${res.status} ${res.statusText}: ${body}`)
  }
  // DELETE endpoints return a small JSON status body too, so this is safe
  // for every call this client makes.
  return res.json() as Promise<T>
}

export const api = {
  listListings: (page: number, pageSize: number, source?: string) => {
    const params = new URLSearchParams({
      page: String(page),
      page_size: String(pageSize),
    })
    if (source) params.set('source', source)
    return request<ListingsPage>(`/api/listings?${params}`)
  },

  listSources: () => request<string[]>('/api/listings/sources'),

  listConnectors: () => request<ConnectorInfo[]>('/api/ingest/connectors'),

  runConnector: (name: string) =>
    request<RunStarted>(`/api/ingest/run/${encodeURIComponent(name)}`, {
      method: 'POST',
    }),

  listRuns: (limit = 20) => request<RunRecord[]>(`/api/ingest/runs?limit=${limit}`),

  listCronJobs: () => request<CronJob[]>('/api/cron'),

  createCronJob: (connector: string, cronExpression: string) =>
    request<CronJob>('/api/cron', {
      method: 'POST',
      body: JSON.stringify({ connector, cron_expression: cronExpression }),
    }),

  pauseCronJob: (id: string) =>
    request<CronJob>(`/api/cron/${id}/pause`, { method: 'POST' }),

  resumeCronJob: (id: string) =>
    request<CronJob>(`/api/cron/${id}/resume`, { method: 'POST' }),

  deleteCronJob: (id: string) =>
    request<{ status: string; id: string }>(`/api/cron/${id}`, {
      method: 'DELETE',
    }),
}

export type { Listing }
