export interface Listing {
  id: string
  source: string
  source_id: string
  title: string | null
  company: string | null
  location: string | null
  posted_at: string | null
  raw: Record<string, unknown>
  ingested_at: string
  last_seen: string
  stale: boolean
}

export interface ListingsPage {
  items: Listing[]
  page: number
  page_size: number
  total: number
}

export interface ConnectorInfo {
  name: string
}

export interface RunStarted {
  status: string
  connector: string
}

export interface RunRecord {
  connector: string
  started_at: string
  finished_at: string | null
  status: 'ok' | 'error' | 'quota_exceeded'
  stats: { seen: number; inserted: number; updated: number } | null
  error: string | null
}

export interface ConnectorUsage {
  connector: string
  calls_used_today: number
  daily_cap: number | null
}

export interface CronJob {
  id: string
  connector: string
  cron_expression: string
  next_run_time: string | null
  paused: boolean
}
