import json
import os
import requests

# ================= CONFIG =================
# ⚠️ TEMPORARY HARDCODED FOR TESTING ONLY
TELEGRAM_BOT_TOKEN = "8308496671:AAF6kDD32Xpk985g0vD6xhWyn2xTQkg6ick"
TELEGRAM_CHAT_ID = "-1003671640198"

# ---------- AI CONFIG ----------
USE_AI = False              # turn True AFTER you buy an API key
OPENAI_API_KEY = ""         # leave empty for now
OPENAI_MODEL = "gpt-4o-mini"
# -----------------------------------------

API_BASE = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

STATE_FILE = "telegram_state.json"
BATCH_FILE = "last_batch.json"

DISABLED_COMMANDS = ["impact", "open", "macro"]


# ================= HELPERS =================

def send_message(text):
    url = f"{API_BASE}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    requests.post(url, json=payload)


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


# ================= AI SUMMARY =================

def ai_summary(title, text):
    if not USE_AI or not OPENAI_API_KEY:
        return None

    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

        prompt = (
            "Summarize the following financial news.\n"
            "Rules:\n"
            "- 3 to 5 bullet points\n"
            "- Neutral, professional tone\n"
            "- Focus on facts and market relevance\n\n"
            f"Title: {title}\n\n"
            f"Article:\n{text}"
        )

        payload = {
            "model": OPENAI_MODEL,
            "messages": [
                {"role": "system", "content": "You are a professional financial analyst."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2
        }

        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=20
        )

        data = r.json()
        return data["choices"][0]["message"]["content"]

    except Exception:
        return None


# ================= MAIN =================

def main():
    last_update_id = get_last_update_id()

    r = requests.get(
        f"{API_BASE}/getUpdates",
        params={"offset": last_update_id + 1, "timeout": 0}
    ).json()

    updates = r.get("result", [])
    if not updates:
        return

    batch = load_last_batch()

    for update in updates:
        update_id = update["update_id"]
        text = update.get("message", {}).get("text", "").strip()

        # ---------- COMMAND DISPATCH ----------
        if text.startswith("//summary"):
            command = "summary"
        elif text.startswith("//why"):
            command = "why"
        elif text.startswith("//impact"):
            command = "impact"
        elif text.startswith("//open"):
            command = "open"
        elif text.startswith("//macro"):
            command = "macro"
        else:
            save_last_update_id(update_id)
            continue
        # ------------------------------------

        parts = text.split()

        # ---------- ARG VALIDATION ----------
        if command in ["summary", "why", "impact", "open"]:
            if len(parts) != 2 or not parts[1].isdigit():
                send_message(
                    "Usage:\n"
                    "<code>//summary 1</code>\n"
                    "<code>//why 1</code>"
                )
                save_last_update_id(update_id)
                continue

            idx = parts[1]
            if idx not in batch:
                send_message("Invalid article number.")
                save_last_update_id(update_id)
                continue

            article = batch[idx]
        else:
            article = None
        # ----------------------------------

        # ---------- DISABLED COMMANDS ----------
        if command in DISABLED_COMMANDS:
            send_message(
                f"⏳ <b>{command}</b> is registered but not enabled yet."
            )
            save_last_update_id(update_id)
            continue
        # --------------------------------------

        # ---------- WHY ----------
        if command == "why":
            title = article.get("title", "").lower()
            reasons = []

            if any(k in title for k in ["fed", "rate", "rates", "inflation", "yield"]):
                reasons.append("Impacts monetary policy expectations and bond yields")

            if any(k in title for k in ["recession", "slowdown", "growth"]):
                reasons.append("Affects risk sentiment and equity positioning")

            if any(k in title for k in ["oil", "energy", "commodity"]):
                reasons.append("May influence inflation dynamics and input costs")

            if not reasons:
                reasons.append("Relevant for overall market positioning")

            reply = "🧠 <b>Why this matters</b>\n\n"
            for r in reasons:
                reply += f"• {r}\n"

            send_message(reply)
            save_last_update_id(update_id)
            continue
        # -------------------------

        # ---------- SUMMARY ----------
        if command == "summary":
            summary_text = ai_summary(
                article.get("title", ""),
                article.get("rss_summary", "")
            )

            if not summary_text:
                summary_text = article.get("rss_summary", "")[:1500]

            reply = (
                f"🧠 <b>Summary</b>\n\n"
                f"<b>{article.get('title','')}</b>\n\n"
                f"{summary_text}\n\n"
                f"<a href=\"{article.get('link','')}\">Read full article →</a>"
            )

            send_message(reply)
            save_last_update_id(update_id)
            continue
        # -----------------------------


if __name__ == "__main__":
    main()
