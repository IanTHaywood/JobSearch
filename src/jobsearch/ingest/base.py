from abc import ABC, abstractmethod
from typing import Iterable


class Connector(ABC):
    """A source of raw job listing JSON.

    Storage is intentionally schema-flexible: a connector just needs to
    yield each source's native JSON shape and say how to identify a
    listing within that source. Normalizing fields across sources is a
    separate, later concern.
    """

    name: str

    # Optional: if the source is known to return newest-first, set this to
    # stop paginating once this many consecutive already-seen listings come
    # back in a row (see pipeline.run_connector). None disables early stop.
    early_stop_after_consecutive_seen: int | None = None

    @abstractmethod
    def fetch(self) -> Iterable[dict]:
        """Yield raw JSON listings from the source."""

    @abstractmethod
    def source_id(self, raw: dict) -> str:
        """Extract the source's own unique ID for a raw listing."""

    def normalize(self, raw: dict) -> dict:
        """Optionally extract cross-source-comparable top-level fields
        (e.g. title, company, location, posted_at) from a raw listing.
        These get merged onto the stored document alongside `raw`, which
        keeps the full original payload intact either way. Default: no
        normalized fields."""
        return {}
