import httpx

from .base import Platform, PlatformError

API = "https://api.telegra.ph"


class Telegraph(Platform):
    """https://telegra.ph/api - works with zero setup (creates an anonymous account)."""
    name = "Telegraph"
    _token_cache = ""

    async def _token(self, client: httpx.AsyncClient) -> str:
        token = self.settings.telegraph_token or Telegraph._token_cache
        if token:
            return token
        r = await client.post(f"{API}/createAccount", json={
            "short_name": "poster", "author_name": self.settings.telegraph_author})
        data = r.json()
        if not data.get("ok"):
            raise PlatformError(f"createAccount failed: {data.get('error')}")
        Telegraph._token_cache = data["result"]["access_token"]
        return Telegraph._token_cache

    async def publish(self, client, message, link):
        token = await self._token(client)
        title = " ".join(message.split()[:8])[:256]
        r = await client.post(f"{API}/createPage", json={
            "access_token": token,
            "title": title,
            "author_name": self.settings.telegraph_author,
            "content": [{"tag": "p", "children": [message]}],
        })
        data = r.json()
        if not data.get("ok"):
            raise PlatformError(f"createPage failed: {data.get('error')}")
        return data["result"]["url"]
