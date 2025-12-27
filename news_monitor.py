import feedparser
import json
import os
import requests

RSS_FEEDS = [
    "https://news.google.com/rss/search?q=financial+markets",
    "https://finance.yahoo.com/rss/topstories",
    "https://feeds.reuters.com/reuters/businessNews",
    "https://www.cnbc.com/id/10000664/device/rss/rss.html"
]

MARKET_KEYWORDS = [
    "financial markets", "equities", "bonds",
    "fixed income", "forex", "commodities", "fx",
    "interest rate", "yield", "central bank", "liquidity", "risk appetite"
]

TOP_COMPANIES = [
    "apple","aapl","microsoft","msft","nvidia","nvda","amazon","amzn",
    "google","googl","alphabet","meta","meta platforms","tesla","tsla",
    "oracle","orcl"
]

MACRO_KEYWORDS = [
    "federal reserve","feds","fed","inflation","cpi","recession",
    "gdp","unemployment","rate hike","rate cut"
]

ALL_KEYWORDS = MARKET_KEYWORDS + TOP_COMPANIES + MACRO_KEYWORDS
SEEN_FILE = "seen.json"

# HELPERS

def is_relevant(text: str) -> bool:
    text = text.lower()
    score = sum(1 for k in ALL_KEYWORDS if k in text)
    return score >= 1


def send_telegram_message(message: str):
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

# LOAD DEDUP STATE

if os.path.exists(SEEN_FILE):
    with open(SEEN_FILE, "r") as f:
        seen = set(json.load(f))
else:
    seen = set()

# FETCH FEEDS

all_entries = []

for url in RSS_FEEDS:
    feed = feedparser.parse(url)
    all_entries.extend(feed.entries)

# BUILD MESSAGE

message = "📊 <b>Market News Update</b>\n\n"

count = 0
MAX_ITEMS = 7

for entry in all_entries:
    title = entry.get("title", "")
    link = entry.get("link", "")

    if not title or not link:
        continue

    # Deduplication
    if link in seen:
        continue

    # Relevance filter
    if not is_relevant(title):
        continue

    message += (
        f"• <b>{title}</b>\n"
        f"<a href=\"{link}\">Read article →</a>\n\n"
    )

    seen.add(link)
    count += 1

    if count >= MAX_ITEMS:
        break

# SEND + SAVE STATE

if count > 0:
    print(message)
    send_telegram_message(message)
else:
    print("No new relevant news.")

with open(SEEN_FILE, "w") as f:
    json.dump(list(seen), f)

