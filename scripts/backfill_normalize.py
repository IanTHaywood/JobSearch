"""One-off backfill: apply each connector's normalize() to already-stored
`raw` documents, so listings ingested before normalize() existed get
title/company/location/posted_at too. Pure local computation — makes zero
API calls, safe to run even for connectors whose quota is exhausted.
"""

from jobsearch.db import LISTINGS_COLLECTION, get_db
from jobsearch.ingest.registry import CONNECTORS


def main() -> None:
    db = get_db()
    listings = db[LISTINGS_COLLECTION]
    connectors = {name: cls() for name, cls in CONNECTORS.items()}

    updated = 0
    skipped_unknown_source = 0
    for doc in listings.find({}, {"source": 1, "raw": 1}):
        connector = connectors.get(doc["source"])
        if connector is None:
            skipped_unknown_source += 1
            continue
        fields = connector.normalize(doc["raw"])
        if not fields:
            continue
        listings.update_one({"_id": doc["_id"]}, {"$set": fields})
        updated += 1

    print(f"updated: {updated}")
    if skipped_unknown_source:
        print(f"skipped (source not in registry): {skipped_unknown_source}")


if __name__ == "__main__":
    main()
