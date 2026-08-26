import os
import time
from typing import Iterable

import requests

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
