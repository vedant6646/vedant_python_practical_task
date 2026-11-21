from .base import Platform


class GitHubGist(Platform):
    """https://docs.github.com/en/rest/gists/gists#create-a-gist"""
    name = "GitHub Gist"
    required_settings = ["github_token"]

    async def publish(self, client, message, link):
        r = await client.post(
            "https://api.github.com/gists",
            headers={
                "Authorization": f"Bearer {self.settings.github_token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            json={"description": message[:200], "public": True,
                  "files": {"post.md": {"content": message}}},
        )
        r.raise_for_status()
        return r.json()["html_url"]
