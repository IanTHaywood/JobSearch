import os
import time
from datetime import datetime, timezone
from typing import Iterable

import requests

from jobsearch.api_usage import record_call
from jobsearch.ingest.base import Connector

API_HOST = "jobs-api14.p.rapidapi.com"
BASE_URL = f"https://{API_HOST}"
REQUEST_DELAY_SECONDS = 1.0


class JobsAPI14Connector(Connector):
    """Base for the RapidAPI "Jobs API" (Pat92/jobs-api14).

    All of its search endpoints (Bing, Indeed, LinkedIn, Xing) share the
    same response envelope (data/meta/_links/errors/warnings) and the
    same meta.nextToken pagination scheme, so subclasses only need to
    set `path` and provide the initial search params.
    """

    path: str
    # RapidAPI calls are metered; stop paginating once this many
    # consecutive already-seen listings come back, on the assumption the
    # source returns newest-first so we've caught up to last run.
    # See api_usage.py for the daily call cap itself.
    early_stop_after_consecutive_seen: int | None = 25

    def initial_params(self) -> dict:
        return {}

    def _headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "x-rapidapi-host": API_HOST,
            "x-rapidapi-key": os.environ["RAPIDAPI_KEY"],
        }

    def fetch(self) -> Iterable[dict]:
        params = {k: v for k, v in self.initial_params().items() if v}
        first_request = True
        while True:
            if not first_request:
                time.sleep(REQUEST_DELAY_SECONDS)
            first_request = False

            record_call(self.name)  # raises DailyQuotaExceeded before firing
            response = requests.get(
                f"{BASE_URL}{self.path}",
                headers=self._headers(),
                params=params,
                timeout=10,
            )
            response.raise_for_status()
            payload = response.json()
            if payload.get("hasError"):
                raise RuntimeError(f"{self.name}: {payload['errors']}")

            yield from payload["data"]

            next_token = payload.get("meta", {}).get("nextToken")
            if not next_token:
                return
            params = {"token": next_token}


class JobsAPI14IndeedConnector(JobsAPI14Connector):
    name = "jobs_api14_indeed"
    path = "/v2/indeed/search"

    def initial_params(self) -> dict:
        return {
            "query": os.environ.get("JOBS_API14_QUERY", "software engineer"),
            "location": os.environ.get("JOBS_API14_LOCATION", ""),
            "countryCode": os.environ.get("JOBS_API14_COUNTRY_CODE", "us"),
        }

    def source_id(self, raw: dict) -> str:
        return raw["id"]

    def normalize(self, raw: dict) -> dict:
        posted_at = None
        ts = raw.get("datePublishedTimestamp")
        if ts:
            posted_at = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
        company = raw.get("company") or {}
        location = raw.get("location") or {}
        return {
            "title": raw.get("title"),
            "company": company.get("name"),
            "location": location.get("location"),
            "posted_at": posted_at,
        }
