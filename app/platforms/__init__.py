from typing import List

from app.config import settings

from .base import Platform
from .bluesky import Bluesky
from .devto import DevTo
from .github_gist import GitHubGist
from .mastodon import Mastodon
from .telegram import Telegram
from .telegraph import Telegraph


def get_platforms() -> List[Platform]:
    """Platform selection is handled internally - add a class here to add a platform."""
    return [Telegraph(settings), Mastodon(settings), Bluesky(settings),
            Telegram(settings), DevTo(settings), GitHubGist(settings)]
