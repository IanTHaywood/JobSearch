"""Smoke test: verify MongoDB is reachable and indexes are set up.

Usage: python scripts/check_connection.py
"""
from jobsearch.db import LISTINGS_COLLECTION, ensure_indexes, get_db


def main() -> None:
    db = get_db()
    db.client.admin.command("ping")
    print(f"Connected to MongoDB, database: {db.name!r}")

    ensure_indexes(db)
    print(f"Indexes on {LISTINGS_COLLECTION!r}:")
    for name, info in db[LISTINGS_COLLECTION].index_information().items():
        print(f"  {name}: {info['key']}")


if __name__ == "__main__":
    main()
