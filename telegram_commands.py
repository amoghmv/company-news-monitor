import json
import os
import requests

# ================= CONFIG =================
# ⚠️ TEMPORARY HARDCODED FOR TESTING ONLY
TELEGRAM_BOT_TOKEN = "8308496671:AAF6kDD32Xpk985g0vD6xhWyn2xTQkg6ick"
TELEGRAM_CHAT_ID = "-1003671640198"
# ========================================

API_BASE = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
STATE_FILE = "telegram_state.json"
BATCH_FILE = "last_batch.json"


def send_message(text):
    url = f"{API_BASE}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    r = requests.post(url, json=payload)
    print("Send status:", r.status_code, r.text)


def get_last_update_id():
    if not os.path.exists(STATE_FILE):
        return 0
    with open(STATE_FILE, "r") as f:
        return json.load(f).get("last_update_id", 0)


def save_last_update_id(update_id):
    with open(STATE_FILE, "w") as f:
        json.dump({"last_update_id": update_id}, f)


def load_last_batch():
    if not os.path.exists(BATCH_FILE):
        return {}
    with open(BATCH_FILE, "r") as f:
        return json.load(f)


def main():
    last_update_id = get_last_update_id()

    url = f"{API_BASE}/getUpdates"
    params = {
        "offset": last_update_id + 1,
        "timeout": 0
    }

    r = requests.get(url, params=params).json()
    updates = r.get("result", [])

    if not updates:
        print("No new Telegram updates.")
        return

    batch = load_last_batch()

    for update in updates:
        update_id = update["update_id"]
        message = update.get("message", {})
        text = message.get("text", "").strip()

        if not text.startswith("//summary"):
            save_last_update_id(update_id)
            continue

        parts = text.split()
        if len(parts) != 2 or not parts[1].isdigit():
            send_message("Usage: <code>//summary 1</code>")
            save_last_update_id(update_id)
            continue

        idx = parts[1]

        if idx not in batch:
            send_message("Invalid article number.")
            save_last_update_id(update_id)
            continue

        article = batch[idx]

        reply = (
            f"🧠 <b>Summary</b>\n\n"
            f"<b>{article.get('title','')}</b>\n\n"
            f"{article.get('rss_summary','')[:1500]}\n\n"
            f"<a href=\"{article.get('link','')}\">Read full article →</a>"
        )

        send_message(reply)
        save_last_update_id(update_id)


if __name__ == "__main__":
    main()
