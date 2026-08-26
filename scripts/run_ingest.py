"""Run a named ingestion connector.

Usage: python scripts/run_ingest.py <connector_name>
"""
import sys

from jobsearch.db import get_db
from jobsearch.ingest.pipeline import run_connector
from jobsearch.ingest.registry import CONNECTORS


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in CONNECTORS:
        names = ", ".join(CONNECTORS) or "(none registered yet)"
        print(f"Usage: python scripts/run_ingest.py <connector_name>\nAvailable: {names}")
        sys.exit(1)

    connector = CONNECTORS[sys.argv[1]]()
    stats = run_connector(connector, get_db())
    print(f"{connector.name}: seen={stats['seen']} inserted={stats['inserted']} updated={stats['updated']}")


if __name__ == "__main__":
    main()
