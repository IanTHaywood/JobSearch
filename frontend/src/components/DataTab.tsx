import { useEffect, useMemo, useState } from 'react'
import { api } from '../api'
import type { Listing, ListingsPage } from '../types'
import { truncate } from '../util'

const PAGE_SIZE = 100

export function DataTab() {
  const [sources, setSources] = useState<string[]>([])
  const [source, setSource] = useState<string>('')
  const [page, setPage] = useState(1)
  const [data, setData] = useState<ListingsPage | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  // Bumped by the Refresh button to re-run the fetch effect below without
  // changing page/source.
  const [reloadToken, setReloadToken] = useState(0)

  useEffect(() => {
    api.listSources().then(setSources).catch(() => setSources([]))
  }, [reloadToken])

  // Reset to page 1 whenever the source filter changes.
  useEffect(() => {
    setPage(1)
  }, [source])

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)
    api
      .listListings(page, PAGE_SIZE, source || undefined)
      .then((res) => {
        if (!cancelled) setData(res)
      })
      .catch((err) => {
        if (!cancelled) setError(String(err))
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [page, source, reloadToken])

  // Raw shape varies per source, so render one column per top-level raw
  // key seen on the current page rather than assuming a fixed schema.
  const rawKeys = useMemo(() => {
    const keys = new Set<string>()
    for (const item of data?.items ?? []) {
      for (const key of Object.keys(item.raw)) keys.add(key)
    }
    return Array.from(keys).sort()
  }, [data])

  const totalPages = data ? Math.max(1, Math.ceil(data.total / PAGE_SIZE)) : 1

  return (
    <div className="tab-panel">
      <div className="toolbar">
        <label>
          Source:{' '}
          <select value={source} onChange={(e) => setSource(e.target.value)}>
            <option value="">All</option>
            {sources.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </label>
        <button onClick={() => setReloadToken((t) => t + 1)} disabled={loading}>
          {loading ? 'Refreshing…' : 'Refresh'}
        </button>
        {data && (
          <span className="muted">
            {data.total.toLocaleString()} listings
          </span>
        )}
      </div>

      {error && <p className="error">Failed to load listings: {error}</p>}

      <div className="table-scroll">
        <table>
          <thead>
            <tr>
              <th>Source</th>
              <th>Source ID</th>
              <th>Ingested</th>
              <th>Last Seen</th>
              {rawKeys.map((key) => (
                <th key={key}>{key}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {(data?.items ?? []).map((item: Listing) => (
              <tr key={item.id}>
                <td>{item.source}</td>
                <td>{truncate(item.source_id)}</td>
                <td>{new Date(item.ingested_at).toLocaleString()}</td>
                <td>{new Date(item.last_seen).toLocaleString()}</td>
                {rawKeys.map((key) => (
                  <td key={key}>{truncate(item.raw[key])}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {loading && <p className="muted">Loading…</p>}

      <div className="toolbar">
        <button disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
          Previous
        </button>
        <span>
          Page {page} of {totalPages}
        </span>
        <button
          disabled={page >= totalPages}
          onClick={() => setPage((p) => p + 1)}
        >
          Next
        </button>
      </div>
    </div>
  )
}
