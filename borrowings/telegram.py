import json

from urllib.request import Request, urlopen
from django.conf import settings


def send_telegram_message(message):
    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID

    if not token or not chat_id:
        raise ValueError("Telegram configuration is missing.")

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": message,
    }

    data = json.dumps(payload).encode("utf-8")

    request = Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urlopen(request, timeout=10) as response:
        result = json.load(response)

    if not result.get("ok"):
        raise RuntimeError("Failed to send Telegram message.")

    return result["result"]
