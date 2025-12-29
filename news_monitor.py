import feedparser
import json
import os
import requests
import hashlib
import re

RSS_FEEDS = [
    "https://seekingalpha.com/market_currents.xml",
    "https://news.google.com/rss/search?q=financial+markets&hl=en-US&gl=US&ceid=US:en",
    "https://finance.yahoo.com/rss/topstories",
    "https://feeds.reuters.com/reuters/businessNews",
    "https://www.cnbc.com/id/10000664/device/rss/rss.html"
]


MARKET_KEYWORDS = [
    "market", "markets",
    "stock", "stocks",
    "equity", "equities",
    "shares",
    "wall street",
    "futures",
    "indexes", "index",
    "nasdaq", "dow", "s&p",
    "volatility",
    "yields", "treasury"
]

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
    return any(k in text for k in ALL_KEYWORDS)


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

def normalize_title(title: str) -> str:
    title = title.lower()

    # remove common prefixes
    title = re.sub(r'^(update|breaking|live|exclusive):\s*', '', title)

    # remove punctuation
    title = re.sub(r'[^a-z0-9\s]', '', title)

    # collapse whitespace
    title = re.sub(r'\s+', ' ', title).strip()

    return title


def fingerprint(entry) -> str:
    title = entry.get("title", "")
    normalized = normalize_title(title)
    return hashlib.md5(normalized.encode("utf-8")).hexdigest()

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
MAX_ITEMS = 5

for entry in all_entries:
    title = entry.get("title", "")
    link = entry.get("link", "")

    if not title or not link:
        continue

    fp = fingerprint(entry)
    if fp in seen:
        continue

    # Relevance filter
    if not is_relevant(title):
        continue

    message += (
        f"• <b>{title}</b>\n"
        f"<a href=\"{link}\">Read article →</a>\n\n"
    )

    seen.add(fp)
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

