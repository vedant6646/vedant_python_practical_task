import asyncio
import logging
from datetime import datetime
from typing import List, Optional

import httpx

from app.config import settings
from app.platforms import get_platforms
from app.platforms.base import Platform, PlatformError
from app.schemas import PostingResult

log = logging.getLogger("posting")
_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; AutoPostingBot/1.0)"}


async def _is_public(client: httpx.AsyncClient, url: str) -> bool:
    """Anonymous GET (no credentials): if it returns < 400, anyone can see it."""
    try:
        r = await client.get(url, headers=_HEADERS, follow_redirects=True, timeout=10)
        return r.status_code < 400
    except Exception:
        return False


def _failed(platform: Platform, error: str) -> PostingResult:
    log.warning("%s FAILED: %s", platform.name, error)
    return PostingResult(platform=platform.name, status="failed", error=error)


async def _post_one(platform: Platform, client: httpx.AsyncClient, message: str, link: str) -> PostingResult:
    missing = platform.missing_credentials()
    if missing:
        return _failed(platform, f"Authentication failed: missing credentials ({', '.join(missing)})")
    try:
        posted_url = await asyncio.wait_for(platform.publish(client, message, link), settings.timeout)
    except PlatformError as e:
        return _failed(platform, str(e))
    except httpx.HTTPStatusError as e:
        code = e.response.status_code
        prefix = "Authentication failed" if code in (401, 403) else f"HTTP {code}"
        return _failed(platform, f"{prefix}: {e.response.text[:200]}")
    except (asyncio.TimeoutError, httpx.TimeoutException):
        return _failed(platform, "Request timed out")
    except httpx.HTTPError as e:
        return _failed(platform, f"Network error: {e.__class__.__name__}: {e}")
    except Exception as e:  # never let one platform break the others
        return _failed(platform, f"Unexpected error: {e.__class__.__name__}: {e}")

    now = datetime.now()
    public = await _is_public(client, posted_url)
    log.info("%s OK -> %s (public=%s)", platform.name, posted_url, public)
    return PostingResult(platform=platform.name, status="success", posted_url=posted_url,
                         public_access=public, date=now.strftime("%Y-%m-%d"),
                         time=now.strftime("%H:%M:%S"))


async def post_to_all(message: str, link: str, platforms: Optional[List[Platform]] = None) -> List[PostingResult]:
    platforms = platforms if platforms is not None else get_platforms()
    async with httpx.AsyncClient(timeout=settings.timeout) as client:
        return list(await asyncio.gather(*(_post_one(p, client, message, link) for p in platforms)))
