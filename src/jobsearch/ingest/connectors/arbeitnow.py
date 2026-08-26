import time
from typing import Iterable

import requests

from jobsearch.ingest.base import Connector

BASE_URL = "https://www.arbeitnow.com/api/job-board-api"
REQUEST_DELAY_SECONDS = 1.5
MAX_RATE_LIMIT_RETRIES = 3


class ArbeitnowConnector(Connector):
    """Free, keyless job board API. https://www.arbeitnow.com/blog/job-board-api

    The API asks callers "please do not abuse" it and has no documented
    rate limit, so requests are paced and back off on 429s rather than
    hammering it as fast as possible.
    """

    name = "arbeitnow"

    def fetch(self) -> Iterable[dict]:
        url = BASE_URL
        first_request = True
        while url:
            if not first_request:
                time.sleep(REQUEST_DELAY_SECONDS)
            first_request = False

            payload = self._get_with_retries(url)
            if payload is None:
                return
            yield from payload["data"]
            url = payload.get("links", {}).get("next")

    def _get_with_retries(self, url: str) -> dict | None:
        for attempt in range(MAX_RATE_LIMIT_RETRIES):
            response = requests.get(url, timeout=10)
            if response.status_code != 429:
                response.raise_for_status()
                return response.json()
            wait = float(response.headers.get("Retry-After", 5 * (attempt + 1)))
            time.sleep(wait)
        return None

    def source_id(self, raw: dict) -> str:
        return raw["slug"]
