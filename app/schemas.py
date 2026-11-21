import re
from typing import List, Literal, Optional
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator

MAX_LENGTH = 200
_URL_CANDIDATE = re.compile(r"(?:https?://|www\.)\S+", re.IGNORECASE)
_TRAILING = ".,;:!?)]}\"'"


def extract_urls(text: str) -> List[str]:
    return [m.group(0).rstrip(_TRAILING) for m in _URL_CANDIDATE.finditer(text)]


def validate_url(url: str) -> None:
    """Raises ValueError with a human-readable reason if the URL is invalid."""
    if not url.lower().startswith(("http://", "https://")):
        raise ValueError("The link must start with http:// or https://")
    parsed = urlparse(url)
    try:
        parsed.port  # raises ValueError on a bad port
    except ValueError:
        raise ValueError("The link has an invalid port")
    host = parsed.hostname or ""
    if not re.fullmatch(r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}", host, re.I):
        raise ValueError(f"'{url}' is not a valid URL (bad domain name)")


class PostingRequest(BaseModel):
    message: str = Field(..., description="Message (max 200 chars) containing exactly one http(s) link")

    @field_validator("message")
    @classmethod
    def check_message(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Message must not be empty")
        if len(v) > MAX_LENGTH:
            raise ValueError(f"Message must not exceed {MAX_LENGTH} characters (got {len(v)})")
        urls = extract_urls(v)
        if len(urls) == 0:
            raise ValueError("Message must contain exactly one CTA link (none found)")
        if len(urls) > 1:
            raise ValueError(f"Message must contain exactly one CTA link ({len(urls)} found)")
        validate_url(urls[0])
        return v

    @property
    def link(self) -> str:
        return extract_urls(self.message)[0]


class PostingResult(BaseModel):
    platform: str
    status: Literal["success", "failed"]
    posted_url: Optional[str] = None
    public_access: bool = False
    date: Optional[str] = None
    time: Optional[str] = None
    error: Optional[str] = None


class PostingResponse(BaseModel):
    success: bool
    results: List[PostingResult]
