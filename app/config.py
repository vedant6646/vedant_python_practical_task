import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    port: int = int(os.getenv("PORT", "4000"))
    timeout: float = float(os.getenv("REQUEST_TIMEOUT", "20"))

    telegraph_token: str = os.getenv("TELEGRAPH_ACCESS_TOKEN", "")
    telegraph_author: str = os.getenv("TELEGRAPH_AUTHOR", "Automated Poster")

    mastodon_base_url: str = os.getenv("MASTODON_BASE_URL", "https://mastodon.social").rstrip("/")
    mastodon_access_token: str = os.getenv("MASTODON_ACCESS_TOKEN", "")

    bluesky_handle: str = os.getenv("BLUESKY_HANDLE", "")
    bluesky_app_password: str = os.getenv("BLUESKY_APP_PASSWORD", "")

    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_chat_id: str = os.getenv("TELEGRAM_CHAT_ID", "")

    devto_api_key: str = os.getenv("DEVTO_API_KEY", "")
    github_token: str = os.getenv("GITHUB_TOKEN", "")


settings = Settings()
