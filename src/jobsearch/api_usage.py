"""Per-connector daily API call budget, tracked independently of the
listing counts in `pipeline.run_connector` — this counts outbound HTTP
requests against a source's rate limit, not listings ingested.

A connector's cap is set via `<CONNECTOR_NAME>_DAILY_CALL_CAP` (name
upper-cased), e.g. JOBS_API14_INDEED_DAILY_CALL_CAP=20. No env var means
no cap — unmetered/free sources like Arbeitnow just don't set one.
"""

import os
from datetime import datetime, timezone

from pymongo import ReturnDocument

from jobsearch.db import get_db

USAGE_COLLECTION = "api_call_usage"


class DailyQuotaExceeded(RuntimeError):
    def __init__(self, connector: str, cap: int, used: int):
        super().__init__(
            f"{connector}: daily API call cap reached ({used}/{cap} used today)"
        )
        self.connector = connector
        self.cap = cap
        self.used = used


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def get_daily_cap(connector: str) -> int | None:
    raw = os.environ.get(f"{connector.upper()}_DAILY_CALL_CAP")
    return int(raw) if raw else None


def calls_used_today(connector: str) -> int:
    doc = get_db()[USAGE_COLLECTION].find_one(
        {"connector": connector, "date": _today()}
    )
    return doc["calls"] if doc else 0


def record_call(connector: str) -> int:
    """Record one outbound API call for `connector` and return today's
    running total. Raises DailyQuotaExceeded *before* recording if the
    cap has already been reached, so the caller never fires the call
    that would exceed it."""
    cap = get_daily_cap(connector)
    used = calls_used_today(connector)
    if cap is not None and used >= cap:
        raise DailyQuotaExceeded(connector, cap, used)
    doc = get_db()[USAGE_COLLECTION].find_one_and_update(
        {"connector": connector, "date": _today()},
        {"$inc": {"calls": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return doc["calls"]
