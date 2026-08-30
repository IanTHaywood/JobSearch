"""Shared connector-execution + APScheduler wiring.

`run_connector_job` is the single entry point both the manual "run now"
endpoint and every cron trigger call, so both paths log to the same
`cron_runs` collection and the UI can show one unified run history.
"""

import logging
from datetime import datetime, timezone
from functools import lru_cache

from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.schedulers.background import BackgroundScheduler

from jobsearch.api_usage import DailyQuotaExceeded
from jobsearch.db import get_client, get_db
from jobsearch.ingest.pipeline import run_connector
from jobsearch.ingest.registry import CONNECTORS

logger = logging.getLogger(__name__)

RUNS_COLLECTION = "cron_runs"
JOBS_COLLECTION = "apscheduler_jobs"


@lru_cache
def get_scheduler() -> BackgroundScheduler:
    jobstore = MongoDBJobStore(
        database=get_db().name, collection=JOBS_COLLECTION, client=get_client()
    )
    scheduler = BackgroundScheduler(jobstores={"default": jobstore})
    scheduler.start()
    return scheduler


def run_connector_job(connector_name: str) -> None:
    """Run one connector and record the outcome. Must stay a top-level,
    picklable function since APScheduler's MongoDBJobStore pickles job
    references for persistence across restarts."""
    db = get_db()
    runs = db[RUNS_COLLECTION]
    started_at = datetime.now(timezone.utc)
    try:
        connector_cls = CONNECTORS[connector_name]
        stats = run_connector(connector_cls(), db)
        runs.insert_one(
            {
                "connector": connector_name,
                "started_at": started_at,
                "finished_at": datetime.now(timezone.utc),
                "status": "ok",
                "stats": stats,
            }
        )
    except DailyQuotaExceeded as exc:
        # Not a bug: the connector's daily call budget (api_usage.py) was
        # already reached, so this run made zero requests.
        runs.insert_one(
            {
                "connector": connector_name,
                "started_at": started_at,
                "finished_at": datetime.now(timezone.utc),
                "status": "quota_exceeded",
                "error": str(exc),
            }
        )
    except Exception as exc:
        logger.exception("run failed for connector %s", connector_name)
        runs.insert_one(
            {
                "connector": connector_name,
                "started_at": started_at,
                "finished_at": datetime.now(timezone.utc),
                "status": "error",
                "error": str(exc),
            }
        )
