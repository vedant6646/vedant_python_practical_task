from datetime import datetime, timezone

from .base import Platform

PDS = "https://bsky.social/xrpc"


class Bluesky(Platform):
    """https://docs.bsky.app/docs/api/com-atproto-repo-create-record (AT Protocol)"""
    name = "Bluesky"
    required_settings = ["bluesky_handle", "bluesky_app_password"]

    async def publish(self, client, message, link):
        s = await client.post(f"{PDS}/com.atproto.server.createSession", json={
            "identifier": self.settings.bluesky_handle,
            "password": self.settings.bluesky_app_password})
        s.raise_for_status()
        session = s.json()

        record = {
            "$type": "app.bsky.feed.post",
            "text": message,
            "createdAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }
        # make the link clickable (facet offsets are UTF-8 byte positions)
        start = message.find(link)
        if start != -1:
            b_start = len(message[:start].encode("utf-8"))
            record["facets"] = [{
                "index": {"byteStart": b_start, "byteEnd": b_start + len(link.encode("utf-8"))},
                "features": [{"$type": "app.bsky.richtext.facet#link", "uri": link}],
            }]

        r = await client.post(
            f"{PDS}/com.atproto.repo.createRecord",
            headers={"Authorization": f"Bearer {session['accessJwt']}"},
            json={"repo": session["did"], "collection": "app.bsky.feed.post", "record": record},
        )
        r.raise_for_status()
        rkey = r.json()["uri"].rsplit("/", 1)[-1]
        return f"https://bsky.app/profile/{session['handle']}/post/{rkey}"
