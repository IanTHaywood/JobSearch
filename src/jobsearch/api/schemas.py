from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class ListingOut(BaseModel):
    id: str
    source: str
    source_id: str
    raw: dict[str, Any]
    ingested_at: datetime
    last_seen: datetime


class ListingsPage(BaseModel):
    items: list[ListingOut]
    page: int
    page_size: int
    total: int


class ConnectorInfo(BaseModel):
    name: str


class RunStarted(BaseModel):
    status: str
    connector: str


class RunOut(BaseModel):
    connector: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    status: str
    stats: Optional[dict[str, Any]] = None
    error: Optional[str] = None


class CronJobIn(BaseModel):
    connector: str
    cron_expression: str  # standard 5-field crontab syntax, e.g. "0 * * * *"


class CronJobOut(BaseModel):
    id: str
    connector: str
    cron_expression: str
    next_run_time: Optional[datetime]
    paused: bool
