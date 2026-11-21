from abc import ABC, abstractmethod
from typing import List

import httpx


class PlatformError(Exception):
    """Raised for expected, readable platform failures."""


class Platform(ABC):
    name: str = "base"
    required_settings: List[str] = []   # names of Settings attributes that must be non-empty

    def __init__(self, settings):
        self.settings = settings

    def missing_credentials(self) -> List[str]:
        return [n.upper() for n in self.required_settings if not getattr(self.settings, n)]

    @abstractmethod
    async def publish(self, client: httpx.AsyncClient, message: str, link: str) -> str:
        """Publish `message` and return the public URL of the new post."""
