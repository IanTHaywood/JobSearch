# JobSearch

Job listing ingestion + a control UI to browse the data and manage API pulls.

## Components

- **MongoDB** — schema-flexible datastore for listings, run via Docker.
- **Ingestion connectors** (`src/jobsearch/ingest/`) — pluggable sources
  (Arbeitnow, RapidAPI jobs-api14/Indeed) that fetch raw listings and
  upsert them, deduped on `(source, source_id)`.
- **API backend** (`src/jobsearch/api/`) — FastAPI service that exposes the
  listings for browsing, lets you trigger a connector run on demand, and
  manages cron-scheduled runs (via APScheduler, persisted in Mongo).
- **Control UI** (`frontend/`) — React + TypeScript app with a Data tab
  (paginated table of stored listings) and an API Control tab (manual
  connector runs + scheduled jobs).

## Running it

1. **Datastore**: `docker compose up -d` (starts Mongo + mongo-express on
   `:8081`).
2. **Backend**: `source .venv/bin/activate && uvicorn jobsearch.api.main:app --reload --port 8000`
3. **Frontend**: `cd frontend && npm run dev` (serves on `:5173`, proxies
   `/api/*` to the backend on `:8000`).

Then open http://localhost:5173.

## Ingestion from the command line

`python scripts/run_ingest.py <connector_name>` still works standalone
(connector names: see `src/jobsearch/ingest/registry.py`), independent of
the API/UI.
