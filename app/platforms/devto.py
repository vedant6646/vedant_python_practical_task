from datetime import datetime

from .base import Platform


class DevTo(Platform):
    """https://developers.forem.com/api/v1#tag/articles/operation/createArticle"""
    name = "DEV Community"
    required_settings = ["devto_api_key"]

    async def publish(self, client, message, link):
        title = f"{' '.join(message.split()[:8])} ({datetime.now():%Y-%m-%d %H:%M})"
        r = await client.post(
            "https://dev.to/api/articles",
            headers={"api-key": self.settings.devto_api_key},
            json={"article": {"title": title, "body_markdown": message, "published": True, "tags": []}},
        )
        r.raise_for_status()
        return r.json()["url"]
