from datetime import datetime, timezone

from pymongo.database import Database

from jobsearch.db import LISTINGS_COLLECTION
from jobsearch.ingest.base import Connector


def run_connector(connector: Connector, db: Database) -> dict:
    """Fetch listings from a connector and upsert them into `listings`.

    Keyed on (source, source_id), matching the unique index from
    ensure_indexes(), so re-running a connector updates existing
    listings' raw data and last_seen instead of duplicating them.

    Also merges each item's connector.normalize(raw) onto the stored
    document (title/company/location/posted_at etc, when a connector
    provides them), and stops early once early_stop_after_consecutive_seen
    already-known listings come back in a row — see Connector for both.
    """
    listings = db[LISTINGS_COLLECTION]
    now = datetime.now(timezone.utc)
    seen = 0
    inserted = 0
    consecutive_seen = 0
    early_stop = connector.early_stop_after_consecutive_seen

    fetch_iter = iter(connector.fetch())
    for raw in fetch_iter:
        update_fields = {"raw": raw, "last_seen": now}
        update_fields.update(connector.normalize(raw))
        result = listings.update_one(
            {"source": connector.name, "source_id": connector.source_id(raw)},
            {
                "$set": update_fields,
                "$setOnInsert": {"ingested_at": now},
            },
            upsert=True,
        )
        seen += 1
        if result.upserted_id is not None:
            inserted += 1
            consecutive_seen = 0
        else:
            consecutive_seen += 1
            if early_stop is not None and consecutive_seen >= early_stop:
                fetch_iter.close()
                break

    return {"seen": seen, "inserted": inserted, "updated": seen - inserted}
