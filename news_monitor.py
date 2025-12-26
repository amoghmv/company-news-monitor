import feedparser
import json
import os
import requests
import subprocess

RSS_URL = "https://news.google.com/rss/search?q=financial+markets"

MARKET_KEYWORDS = [
    "stock", "stocks", "equity", "equities",
    "share", "shares", "index", "indices",
    "market", "markets"
]

EVENT_KEYWORDS = [
    "earnings", "results", "guidance",
    "ipo", "listing", "delisting",
    "merger", "acquisition", "m&a",
    "buyback", "dividend", "split",
    "downgrade", "upgrade",
    "sec", "lawsuit", "antitrust"
]

MACRO_KEYWORDS = [
    "interest rates", "inflation", "cpi",
    "federal reserve", "fed",
    "central bank", "recession",
    "gdp", "unemployment",
    "bond yields", "treasury"
]

ALL_KEYWORDS = (
    MARKET_KEYWORDS +
    EVENT_KEYWORDS +
    MACRO_KEYWORDS
)

def is_relevant(text):
    text = text.lower()
    score = sum(1 for k in ALL_KEYWORDS if k in text)
    return score >= 1

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

