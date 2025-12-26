import feedparser
import json
import os
import requests
import subprocess

RSS_URL = "https://news.google.com/rss/search?q=Apple+stock"

def send_telegram_message(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("Telegram credentials missing")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }

    r = requests.post(url, data=payload)
    print("Telegram status:", r.status_code, r.text)

feed = feedparser.parse(RSS_URL)

message = "🧪 TEST NEWS DELIVERY\n\n"

for entry in feed.entries[:5]:
    message += f"- {entry.title}\n"

print(message)
send_telegram_message(message)

