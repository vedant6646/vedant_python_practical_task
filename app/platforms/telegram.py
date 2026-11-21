from .base import Platform, PlatformError


class Telegram(Platform):
    """https://core.telegram.org/bots/api#sendmessage  (post to a public channel)"""
    name = "Telegram"
    required_settings = ["telegram_bot_token", "telegram_chat_id"]

    async def publish(self, client, message, link):
        r = await client.post(
            f"https://api.telegram.org/bot{self.settings.telegram_bot_token}/sendMessage",
            json={"chat_id": self.settings.telegram_chat_id, "text": message},
        )
        data = r.json()
        if not data.get("ok"):
            raise PlatformError(f"Telegram: {data.get('description', 'unknown error')}")
        msg = data["result"]
        chat = msg["chat"]
        if chat.get("username"):
            return f"https://t.me/{chat['username']}/{msg['message_id']}"
        # private channel: link only works for members
        return f"https://t.me/c/{str(chat['id']).replace('-100', '', 1)}/{msg['message_id']}"
