import { useEffect, useState } from 'react'
import { api } from '../api'
import type { ConnectorInfo, ConnectorUsage, CronJob, RunRecord } from '../types'

const RUN_POLL_MS = 5000

export function ApiControlTab() {
  const [connectors, setConnectors] = useState<ConnectorInfo[]>([])
  const [selectedConnector, setSelectedConnector] = useState('')
  const [usage, setUsage] = useState<ConnectorUsage[]>([])
  const [runs, setRuns] = useState<RunRecord[]>([])
  const [runError, setRunError] = useState<string | null>(null)
  const [triggering, setTriggering] = useState(false)

  const [cronJobs, setCronJobs] = useState<CronJob[]>([])
  const [cronConnector, setCronConnector] = useState('')
  const [cronExpression, setCronExpression] = useState('')
  const [cronError, setCronError] = useState<string | null>(null)

  const refreshRuns = () => {
    api.listRuns(20).then(setRuns).catch((err) => setRunError(String(err)))
  }
  const refreshUsage = () => {
    api.listUsage().then(setUsage).catch(() => {})
  }
  const refreshCronJobs = () => {
    api.listCronJobs().then(setCronJobs).catch((err) => setCronError(String(err)))
  }

  useEffect(() => {
    api.listConnectors().then((list) => {
      setConnectors(list)
      if (list.length > 0) {
        setSelectedConnector(list[0].name)
        setCronConnector(list[0].name)
      }
    })
    refreshRuns()
    refreshCronJobs()
    refreshUsage()
    const interval = setInterval(() => {
      refreshRuns()
      refreshUsage()
    }, RUN_POLL_MS)
    return () => clearInterval(interval)
  }, [])

  const handleRunNow = async () => {
    if (!selectedConnector) return
    setTriggering(true)
    setRunError(null)
    try {
      await api.runConnector(selectedConnector)
      // Give the background task a moment to at least start, then refresh.
      setTimeout(() => {
        refreshRuns()
        refreshUsage()
      }, 500)
    } catch (err) {
      setRunError(String(err))
    } finally {
      setTriggering(false)
    }
  }

  const handleCreateCronJob = async () => {
    if (!cronConnector || !cronExpression.trim()) return
    setCronError(null)
    try {
      await api.createCronJob(cronConnector, cronExpression.trim())
      setCronExpression('')
      refreshCronJobs()
    } catch (err) {
      setCronError(String(err))
    }
  }

  const handlePauseResume = async (job: CronJob) => {
    try {
      if (job.paused) {
        await api.resumeCronJob(job.id)
      } else {
        await api.pauseCronJob(job.id)
      }
      refreshCronJobs()
    } catch (err) {
      setCronError(String(err))
    }
  }

  const handleDelete = async (job: CronJob) => {
    try {
      await api.deleteCronJob(job.id)
      refreshCronJobs()
    } catch (err) {
      setCronError(String(err))
    }
  }

  return (
    <div className="tab-panel">
      <section>
        <h2>Manual request</h2>
        <p className="muted">
          Runs a connector immediately in the background. Check any API
          quota before running a metered connector.
        </p>
        <div className="toolbar">
          <select
            value={selectedConnector}
            onChange={(e) => setSelectedConnector(e.target.value)}
          >
            {connectors.map((c) => (
              <option key={c.name} value={c.name}>
                {c.name}
              </option>
            ))}
          </select>
          <button onClick={handleRunNow} disabled={triggering || !selectedConnector}>
            {triggering ? 'Starting…' : 'Run now'}
          </button>
          <button onClick={refreshRuns}>Refresh history</button>
        </div>
        {runError && <p className="error">{runError}</p>}

        <div className="usage-row">
          {usage.map((u) => (
            <span key={u.connector} className="usage-pill">
              <strong>{u.connector}</strong>:{' '}
              {u.daily_cap != null
                ? `${u.calls_used_today} / ${u.daily_cap} calls today`
                : `${u.calls_used_today} calls today (no cap set)`}
            </span>
          ))}
        </div>

        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Connector</th>
                <th>Started</th>
                <th>Finished</th>
                <th>Status</th>
                <th>Result</th>
              </tr>
            </thead>
            <tbody>
              {runs.map((run, i) => (
                <tr key={i}>
                  <td>{run.connector}</td>
                  <td>{new Date(run.started_at).toLocaleString()}</td>
                  <td>{run.finished_at ? new Date(run.finished_at).toLocaleString() : '—'}</td>
                  <td className={run.status !== 'ok' ? 'error' : ''}>{run.status}</td>
                  <td>
                    {run.stats
                      ? `seen ${run.stats.seen}, inserted ${run.stats.inserted}, updated ${run.stats.updated}`
                      : run.error ?? ''}
                  </td>
                </tr>
              ))}
              {runs.length === 0 && (
                <tr>
                  <td colSpan={5} className="muted">
                    No runs yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <h2>Scheduled jobs</h2>
        <p className="muted">
          Standard 5-field crontab syntax (minute hour day month weekday), e.g.{' '}
          <code>0 * * * *</code> for hourly.
        </p>
        <div className="toolbar">
          <select
            value={cronConnector}
            onChange={(e) => setCronConnector(e.target.value)}
          >
            {connectors.map((c) => (
              <option key={c.name} value={c.name}>
                {c.name}
              </option>
            ))}
          </select>
          <input
            type="text"
            placeholder="0 * * * *"
            value={cronExpression}
            onChange={(e) => setCronExpression(e.target.value)}
          />
          <button onClick={handleCreateCronJob} disabled={!cronExpression.trim()}>
            Add schedule
          </button>
        </div>
        {cronError && <p className="error">{cronError}</p>}

        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Connector</th>
                <th>Schedule</th>
                <th>Next run</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {cronJobs.map((job) => (
                <tr key={job.id}>
                  <td>{job.connector}</td>
                  <td>
                    <code>{job.cron_expression}</code>
                  </td>
                  <td>{job.next_run_time ? new Date(job.next_run_time).toLocaleString() : '—'}</td>
                  <td>{job.paused ? 'Paused' : 'Active'}</td>
                  <td>
                    <button onClick={() => handlePauseResume(job)}>
                      {job.paused ? 'Resume' : 'Pause'}
                    </button>{' '}
                    <button onClick={() => handleDelete(job)}>Delete</button>
                  </td>
                </tr>
              ))}
              {cronJobs.length === 0 && (
                <tr>
                  <td colSpan={5} className="muted">
                    No scheduled jobs.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  )
}
