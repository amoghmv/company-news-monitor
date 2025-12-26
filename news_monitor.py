import feedparser
import json
import os
import requests
import subprocess

RSS_FEEDS = [
    "https://news.google.com/rss/search?q=stock+market",
    "https://finance.yahoo.com/rss/topstories",
    "https://feeds.reuters.com/reuters/businessNews",
    "https://www.cnbc.com/id/10000664/device/rss/rss.html"
]

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

ALL_KEYWORDS = MARKET_KEYWORDS + EVENT_KEYWORDS + MACRO_KEYWORDS
SEEN_FILE = "seen.json"

def is_relevant(text):
    text = text.lower()
    score = sum(1 for k in ALL_KEYWORDS if k in text)
    return score >= 1


def get_source(entry):
    link = entry.get("link", "").lower()

    if "reuters" in link:
        return "Reuters"
    if "yahoo" in link:
        return "Yahoo Finance"
    if "cnbc" in link:
        return "CNBC"
    if "bloomberg" in link:
        return "Bloomberg"
    if "google.com" in link:
        return "Google News"

    return "News"


def send_telegram_message(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("Telegram credentials missing")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }

    r = requests.post(url, data=payload)
    print("Telegram status:", r.status_code, r.text)

# --------------------------------
# - seen.json
# - is_relevant()
# - deduplication
# --------------------------------

all_entries = []

for url in RSS_FEEDS:
    feed = feedparser.parse(url)
    all_entries.extend(feed.entries)

message = "📊 <b>Market News Update (TEST MODE)</b>\n\n"

count = 0
for entry in all_entries:
    title = entry.get("title", "")
    link = entry.get("link", "")

    if not title or not link:
        continue

    
    # if not is_relevant(title):
    #     continue

    source = get_source(entry)

    message += (
        f"• <b>[{source}]</b>\n"
        f"<a href=\"{link}\">{title}</a>\n\n"
    )

    count += 1
    if count >= 15:
        break

print(message)
send_telegram_message(message)
