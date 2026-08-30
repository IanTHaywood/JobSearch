export interface Listing {
  id: string
  source: string
  source_id: string
  raw: Record<string, unknown>
  ingested_at: string
  last_seen: string
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
  status: 'ok' | 'error'
  stats: { seen: number; inserted: number; updated: number } | null
  error: string | null
}

export interface CronJob {
  id: string
  connector: string
  cron_expression: string
  next_run_time: string | null
  paused: boolean
}
