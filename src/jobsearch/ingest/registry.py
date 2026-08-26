from jobsearch.ingest.base import Connector
from jobsearch.ingest.connectors.arbeitnow import ArbeitnowConnector

CONNECTORS: dict[str, type[Connector]] = {
    "arbeitnow": ArbeitnowConnector,
}
