import os
from functools import lru_cache

from dotenv import load_dotenv
from pymongo import ASCENDING, MongoClient
from pymongo.database import Database

load_dotenv()

LISTINGS_COLLECTION = "listings"


@lru_cache
def get_client() -> MongoClient:
    # tz_aware so datetimes read back from Mongo are UTC-aware, matching
    # the datetime.now(timezone.utc) values the app writes — otherwise
    # comparing a stored value against a fresh aware datetime raises.
    return MongoClient(os.environ["MONGO_URI"], tz_aware=True)


def get_db() -> Database:
    db_name = os.environ.get("MONGO_DB_NAME", "jobsearch")
    return get_client()[db_name]


def ensure_indexes(db: Database | None = None) -> None:
    """Create indexes needed for ingestion (dedup) and querying."""
    db = get_db() if db is None else db
    listings = db[LISTINGS_COLLECTION]
    # Each source assigns its own IDs; (source, source_id) is the natural
    # dedup key across independent, differently-shaped ingestion feeds.
    listings.create_index(
        [("source", ASCENDING), ("source_id", ASCENDING)], unique=True
    )
    listings.create_index([("ingested_at", ASCENDING)])
