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
    print("Send status:", r.status_code)


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

    response = requests.get(url, params=params).json()
    updates = response.get("result", [])

    if not updates:
        print("No new Telegram updates.")
        return

    batch = load_last_batch()

    for update in updates:
        update_id = update["update_id"]
        message = update.get("message", {})
        text = message.get("text", "").strip()

        # ---------- COMMAND DISPATCH ----------
        if text.startswith("//summary"):
            command = "summary"
        elif text.startswith("//why"):
            command = "why"
        else:
            save_last_update_id(update_id)
            continue
        # --------------------------------------

        parts = text.split()
        if len(parts) != 2 or not parts[1].isdigit():
            send_message("Usage: <code>//summary 1</code> or <code>//why 1</code>")
            save_last_update_id(update_id)
            continue

        idx = parts[1]

        if idx not in batch:
            send_message("Invalid article number.")
            save_last_update_id(update_id)
            continue

        article = batch[idx]

        # ---------- WHY COMMAND ----------
        if command == "why":
            title = article.get("title", "").lower()
            reasons = []

            if any(k in title for k in ["fed", "rate", "rates", "inflation", "yield"]):
                reasons.append("Signals potential shifts in monetary policy expectations")
                reasons.append("Direct impact on bond yields and rate-sensitive equities")

            if any(k in title for k in ["recession", "slowdown", "growth"]):
                reasons.append("Raises concerns about economic growth momentum")
                reasons.append("Negative for risk assets and cyclicals")

            if any(k in title for k in ["oil", "energy", "commodity"]):
                reasons.append("Could influence inflation dynamics and input costs")

            if not reasons:
                reasons.append("Relevant for overall market sentiment and positioning")

            reply = "🧠 <b>Why this matters</b>\n\n"
            for r in reasons:
                reply += f"• {r}\n"

            send_message(reply)
            save_last_update_id(update_id)
            continue
        # --------------------------------

        # ---------- SUMMARY COMMAND ----------
        if command == "summary":
            reply = (
                f"🧠 <b>Summary</b>\n\n"
                f"<b>{article.get('title','')}</b>\n\n"
                f"{article.get('rss_summary','')[:1500]}\n\n"
                f"<a href=\"{article.get('link','')}\">Read full article →</a>"
            )

            send_message(reply)
            save_last_update_id(update_id)
            continue
        # ------------------------------------


if __name__ == "__main__":
    main()
