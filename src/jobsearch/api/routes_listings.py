import os
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Query

from jobsearch.api.schemas import ListingOut, ListingsPage
from jobsearch.db import LISTINGS_COLLECTION, get_db

router = APIRouter(prefix="/api/listings", tags=["listings"])

# A listing not re-seen by its connector in this many days is considered
# stale (likely expired/filled) even though we never got an explicit
# "removed" signal from the source. Configurable, defaults to 5 days.
STALE_AFTER_DAYS = int(os.environ.get("STALE_AFTER_DAYS", "5"))


@router.get("", response_model=ListingsPage)
def list_listings(
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=500),
    source: str | None = None,
    hide_stale: bool = False,
) -> ListingsPage:
    db = get_db()
    listings = db[LISTINGS_COLLECTION]
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=STALE_AFTER_DAYS)

    query: dict = {}
    if source:
        query["source"] = source
    if hide_stale:
        query["last_seen"] = {"$gte": cutoff}

    total = listings.count_documents(query)
    skip = (page - 1) * page_size
    cursor = listings.find(query).sort("ingested_at", -1).skip(skip).limit(page_size)
    items = [
        ListingOut(
            id=str(doc["_id"]),
            source=doc["source"],
            source_id=doc["source_id"],
            title=doc.get("title"),
            company=doc.get("company"),
            location=doc.get("location"),
            posted_at=doc.get("posted_at"),
            raw=doc["raw"],
            ingested_at=doc["ingested_at"],
            last_seen=doc["last_seen"],
            stale=doc["last_seen"] < cutoff,
        )
        for doc in cursor
    ]
    return ListingsPage(items=items, page=page, page_size=page_size, total=total)


@router.get("/sources", response_model=list[str])
def list_sources() -> list[str]:
    db = get_db()
    return db[LISTINGS_COLLECTION].distinct("source")
