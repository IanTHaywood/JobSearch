from fastapi import APIRouter, Query

from jobsearch.api.schemas import ListingOut, ListingsPage
from jobsearch.db import LISTINGS_COLLECTION, get_db

router = APIRouter(prefix="/api/listings", tags=["listings"])


@router.get("", response_model=ListingsPage)
def list_listings(
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=500),
    source: str | None = None,
) -> ListingsPage:
    db = get_db()
    listings = db[LISTINGS_COLLECTION]
    query = {"source": source} if source else {}
    total = listings.count_documents(query)
    skip = (page - 1) * page_size
    cursor = listings.find(query).sort("ingested_at", -1).skip(skip).limit(page_size)
    items = [
        ListingOut(
            id=str(doc["_id"]),
            source=doc["source"],
            source_id=doc["source_id"],
            raw=doc["raw"],
            ingested_at=doc["ingested_at"],
            last_seen=doc["last_seen"],
        )
        for doc in cursor
    ]
    return ListingsPage(items=items, page=page, page_size=page_size, total=total)


@router.get("/sources", response_model=list[str])
def list_sources() -> list[str]:
    db = get_db()
    return db[LISTINGS_COLLECTION].distinct("source")
