from fastapi import APIRouter, BackgroundTasks, HTTPException, Query

from jobsearch.api.scheduler import RUNS_COLLECTION, run_connector_job
from jobsearch.api.schemas import ConnectorInfo, ConnectorUsage, RunOut, RunStarted
from jobsearch.api_usage import calls_used_today, get_daily_cap
from jobsearch.db import get_db
from jobsearch.ingest.registry import CONNECTORS

router = APIRouter(prefix="/api/ingest", tags=["ingest"])


@router.get("/connectors", response_model=list[ConnectorInfo])
def list_connectors() -> list[ConnectorInfo]:
    return [ConnectorInfo(name=name) for name in CONNECTORS]


@router.get("/usage", response_model=list[ConnectorUsage])
def list_usage() -> list[ConnectorUsage]:
    return [
        ConnectorUsage(
            connector=name,
            calls_used_today=calls_used_today(name),
            daily_cap=get_daily_cap(name),
        )
        for name in CONNECTORS
    ]


@router.post("/run/{connector_name}", response_model=RunStarted)
def run_connector_now(
    connector_name: str, background_tasks: BackgroundTasks
) -> RunStarted:
    """Kick off a connector run in the background. Fetching + upserting
    can take well over a minute (rate-limit pacing), so this returns
    immediately; poll GET /api/ingest/runs for the outcome."""
    if connector_name not in CONNECTORS:
        raise HTTPException(404, f"Unknown connector: {connector_name}")
    background_tasks.add_task(run_connector_job, connector_name)
    return RunStarted(status="started", connector=connector_name)


@router.get("/runs", response_model=list[RunOut])
def list_runs(limit: int = Query(20, ge=1, le=200)) -> list[RunOut]:
    db = get_db()
    cursor = db[RUNS_COLLECTION].find().sort("started_at", -1).limit(limit)
    return [RunOut(**doc) for doc in cursor]
