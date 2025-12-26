import feedparser
import json
import os
import requests
import subprocess

COMPANY = "Apple"
KEYWORDS = ["Apple", "AAPL", "Tim Cook", "iPhone"]

RSS_URL = f"https://news.google.com/rss/search?q={COMPANY}+stock"
SEEN_FILE = "seen.json"

def is_relevant(text):
    return any(k.lower() in text.lower() for k in KEYWORDS)

def send_telegram_message(message):
    token = os.getenv("8269638873:AAHExLZrAFPhQhxLvLnExMw5S_Tu3FDouKU")
    chat_id = os.getenv("7901236064")

    if not token or not chat_id:
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }

    requests.post(url, data=payload)
    
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

import subprocess

# Commit updated seen.json back to repo (only if running on GitHub Actions)
if os.getenv("GITHUB_ACTIONS") == "true":
    subprocess.run(["git", "config", "user.name", "github-actions"])
    subprocess.run(["git", "config", "user.email", "actions@github.com"])
    subprocess.run(["git", "add", "seen.json"])
    subprocess.run(["git", "commit", "-m", "Update seen news"], check=False)
    subprocess.run(["git", "push"], check=False)
