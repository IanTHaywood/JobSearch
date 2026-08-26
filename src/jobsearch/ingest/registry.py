from jobsearch.ingest.base import Connector
from jobsearch.ingest.connectors.arbeitnow import ArbeitnowConnector
from jobsearch.ingest.connectors.jobs_api14 import JobsAPI14IndeedConnector

CONNECTORS: dict[str, type[Connector]] = {
    "arbeitnow": ArbeitnowConnector,
    "jobs_api14_indeed": JobsAPI14IndeedConnector,
}
