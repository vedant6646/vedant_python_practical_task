from .base import Platform


class Mastodon(Platform):
    """https://docs.joinmastodon.org/methods/statuses/#create"""
    name = "Mastodon"
    required_settings = ["mastodon_access_token"]

    async def publish(self, client, message, link):
        r = await client.post(
            f"{self.settings.mastodon_base_url}/api/v1/statuses",
            headers={"Authorization": f"Bearer {self.settings.mastodon_access_token}"},
            json={"status": message, "visibility": "public"},
        )
        r.raise_for_status()
        return r.json()["url"]
