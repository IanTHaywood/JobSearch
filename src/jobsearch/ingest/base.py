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

    @abstractmethod
    def fetch(self) -> Iterable[dict]:
        """Yield raw JSON listings from the source."""

    @abstractmethod
    def source_id(self, raw: dict) -> str:
        """Extract the source's own unique ID for a raw listing."""
