import feedparser
import json
import os
import requests
import hashlib
import re

TELEGRAM_BOT_TOKEN = "8308496671:AAF6kDD32Xpk985g0vD6xhWyn2xTQkg6ick"
TELEGRAM_CHAT_ID = "-1003671640198"

RSS_FEEDS = [
    "https://news.google.com/rss/search?q=markets&hl=en-US&gl=US&ceid=US:en",
    "https://finance.yahoo.com/rss/topstories",
    "https://feeds.reuters.com/reuters/businessNews",
    "https://www.cnbc.com/id/10000664/device/rss/rss.html"
]

MARKET_KEYWORDS = [
    "market", "markets",
    "stock", "stocks",
    "shares",
    "wall street",
    "futures",
    "dow", "nasdaq", "s&p",
    "index", "indexes",
    "yields", "treasury",
    "bond", "bonds",
    "volatility",
    "selloff", "rally"
]

TOP_COMPANIES = [
    "apple","aapl","microsoft","msft","nvidia","nvda",
    "amazon","amzn","google","googl","alphabet",
    "meta","tesla","tsla","oracle","orcl"
]

MACRO_KEYWORDS = [
    "fed", "federal reserve",
    "inflation", "cpi",
    "recession", "gdp",
    "unemployment",
    "rate hike", "rate cut",
    "interest rate"
]

ALL_KEYWORDS = MARKET_KEYWORDS + TOP_COMPANIES + MACRO_KEYWORDS

SEEN_FILE = "seen.json"
LAST_BATCH_FILE = "last_batch.json"

def is_relevant(text: str) -> bool:
    text = text.lower()
    return any(k in text for k in ALL_KEYWORDS)


def normalize_title(title: str) -> str:
    title = title.lower()
    title = re.sub(r'^(update|breaking|live|exclusive):\s*', '', title)
    title = re.sub(r'[^a-z0-9\s]', '', title)
    title = re.sub(r'\s+', ' ', title).strip()
    return title


def fingerprint(entry) -> str:
    normalized = normalize_title(entry.get("title", ""))
    return hashlib.md5(normalized.encode("utf-8")).hexdigest()

def send_telegram_message(message: str, article_id: str = None, article_link: str = None):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }

    if article_id:
    payload["reply_markup"] = {
        "inline_keyboard": [
            [
                {"text": "Summary", "switch_inline_query_current_chat": f"//summary {article_id}"},
                {"text": "Why", "switch_inline_query_current_chat": f"//why {article_id}"},
                {"text": "Open", "url": article_link}
            ]
        ]
    }

    requests.post(url, json=payload)


# LOAD DEDUP STATE

if os.path.exists(SEEN_FILE):
    with open(SEEN_FILE, "r") as f:
        seen = set(json.load(f))
else:
    seen = set()


all_entries = []
for url in RSS_FEEDS:
    feed = feedparser.parse(url)
    all_entries.extend(feed.entries)


message = "📊 <b>Market News Update</b>\n\n"
count = 0
last_batch = {}
MAX_ITEMS = 7

for entry in all_entries:
    title = entry.get("title", "")
    link = entry.get("link", "")

    if not title or not link:
        continue

    fp = fingerprint(entry)
    if fp in seen:
        continue

    if not is_relevant(title):
        continue

    message += (
        f"• <b>{title}</b>\n"
        f"<a href=\"{link}\">Read article →</a>\n\n"
    )

    seen.add(fp)
    count += 1

    article_id = str(count)
    last_batch[article_id] = {
        "title": title,
        "link": link,
        "rss_summary": entry.get("summary", ""),
        "fingerprint": fp
    }

    if count >= MAX_ITEMS:
        break


# SEND + SAVE STATE

if count > 0:
    print(message)
    send_telegram_message(message, article_id)
else:
    print("No new relevant news.")

with open(SEEN_FILE, "w") as f:
    json.dump(list(seen), f)

with open(LAST_BATCH_FILE, "w") as f:
    json.dump(last_batch, f, indent=2)

