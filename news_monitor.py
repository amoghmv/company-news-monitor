import feedparser
import json
import os

COMPANY = "Apple"
KEYWORDS = ["Apple", "AAPL", "Tim Cook", "iPhone"]

RSS_URL = f"https://news.google.com/rss/search?q={COMPANY}+stock"
SEEN_FILE = "seen.json"

def is_relevant(text):
    return any(k.lower() in text.lower() for k in KEYWORDS)


if os.path.exists(SEEN_FILE):
    seen = set(json.load(open(SEEN_FILE)))
else:
    seen = set()

feed = feedparser.parse(RSS_URL)

new_items = []

for entry in feed.entries:
    if entry.link not in seen and is_relevant(entry.title):
        new_items.append(entry)
        seen.add(entry.link)

json.dump(list(seen), open(SEEN_FILE, "w"))

if not new_items:
    print("No new relevant news.")
    exit()

print("New company news:\n")
for item in new_items:
    print("-", item.title)