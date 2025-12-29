import feedparser
import json
import os
import requests
import hashlib
import re

# =========================
# RSS FEEDS
# =========================

RSS_FEEDS = [
    "https://seekingalpha.com/market_currents.xml",
    "https://news.google.com/rss/search?q=markets&hl=en-US&gl=US&ceid=US:en",
    "https://finance.yahoo.com/rss/topstories",
    "https://feeds.reuters.com/reuters/businessNews",
    "https://www.cnbc.com/id/10000664/device/rss/rss.html"
]

SEEN_FILE = "seen.json"

# =========================
# HELPERS (kept, not used)
# =========================

def is_relevant(text: str) -> bool:
    text = text.lower()
    return True  # FILTER HASHED OUT


def normalize_title(title: str) -> str:
    title = title.lower()
    title = re.sub(r'^(update|breaking|live|exclusive):\s*', '', title)
    title = re.sub(r'[^a-z0-9\s]', '', title)
    title = re.sub(r'\s+', ' ', title).strip()
    return title


def fingerprint(entry) -> str:
    normalized = normalize_title(entry.get("title", ""))
    return hashlib.md5(normalized.encode("utf-8")).hexdigest()


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

# =========================
# LOAD STATE (HASHED OUT)
# =========================

# if os.path.exists(SEEN_FILE):
#     with open(SEEN_FILE, "r") as f:
#         seen = set(json.load(f))
# else:
#     seen = set()

# =========================
# FETCH FEEDS
# =========================

all_entries = []

for url in RSS_FEEDS:
    feed = feedparser.parse(url)
    all_entries.extend(feed.entries)

# =========================
# BUILD MESSAGE (NO FILTERS)
# =========================

message = "📊 <b>Market News Update (NO FILTERS)</b>\n\n"

count = 0
MAX_ITEMS = 10

for entry in all_entries:
    title = entry.get("title", "")
    link = entry.get("link", "")

    if not title or not link:
        continue

    # fp = fingerprint(entry)
    # if fp in seen:
    #     continue

    # if not is_relevant(title):
    #     continue

    message += (
        f"• <b>{title}</b>\n"
        f"<a href=\"{link}\">Read article →</a>\n\n"
    )

    # seen.add(fp)
    count += 1

    if count >= MAX_ITEMS:
        break

# =========================
# SEND MESSAGE
# =========================

if count > 0:
    print(message)
    send_telegram_message(message)
else:
    print("No news found.")

# =========================
# SAVE STATE (HASHED OUT)
# =========================

# with open(SEEN_FILE, "w") as f:
#     json.dump(list(seen), f)
