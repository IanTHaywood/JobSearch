from datetime import datetime, timezone

from pymongo.database import Database

from jobsearch.db import LISTINGS_COLLECTION
from jobsearch.ingest.base import Connector


def run_connector(connector: Connector, db: Database) -> dict:
    """Fetch listings from a connector and upsert them into `listings`.

    Keyed on (source, source_id), matching the unique index from
    ensure_indexes(), so re-running a connector updates existing
    listings' raw data and last_seen instead of duplicating them.
    """
    listings = db[LISTINGS_COLLECTION]
    now = datetime.now(timezone.utc)
    seen = 0
    inserted = 0

    for raw in connector.fetch():
        result = listings.update_one(
            {"source": connector.name, "source_id": connector.source_id(raw)},
            {
                "$set": {"raw": raw, "last_seen": now},
                "$setOnInsert": {"ingested_at": now},
            },
            upsert=True,
        )
        seen += 1
        if result.upserted_id is not None:
            inserted += 1

    return {"seen": seen, "inserted": inserted, "updated": seen - inserted}
