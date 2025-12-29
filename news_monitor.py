import feedparser
import requests

# =========================
# 🔐 HARDCODED TELEGRAM CONFIG
# =========================

TELEGRAM_BOT_TOKEN = "8308496671:AAF6kDD32Xpk985g0vD6xhWyn2xTQkg6ick"
TELEGRAM_CHAT_ID = "-1003671640198"

# =========================
# RSS FEEDS (KNOWN TO WORK)
# =========================

RSS_FEEDS = [
    "https://news.google.com/rss/search?q=markets&hl=en-US&gl=US&ceid=US:en",
    "https://finance.yahoo.com/rss/topstories",
    "https://feeds.reuters.com/reuters/businessNews",
    "https://www.cnbc.com/id/10000664/device/rss/rss.html"
]

# =========================
# TELEGRAM SENDER
# =========================

def send_telegram_message(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }

    r = requests.post(url, data=payload)
    print("Telegram status:", r.status_code, r.text)

# =========================
# FETCH NEWS
# =========================

all_entries = []

for url in RSS_FEEDS:
    feed = feedparser.parse(url)
    all_entries.extend(feed.entries)

# =========================
# BUILD MESSAGE (NO FILTERS)
# =========================

message = "📊 <b>Market News Update (HARDCODE TEST)</b>\n\n"

count = 0
MAX_ITEMS = 10

for entry in all_entries:
    title = entry.get("title", "")
    link = entry.get("link", "")

    if not title or not link:
        continue

    message += (
        f"• <b>{title}</b>\n"
        f"<a href=\"{link}\">Read article →</a>\n\n"
    )

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
