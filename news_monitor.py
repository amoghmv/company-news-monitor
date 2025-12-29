import os
import requests

print("=== ENV CHECK ===")
print("BOT TOKEN:", os.getenv("TELEGRAM_BOT_TOKEN"))
print("CHAT ID:", os.getenv("TELEGRAM_CHAT_ID"))

token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")

if not token or not chat_id:
    raise RuntimeError("❌ Secrets are NOT available to the workflow")

url = f"https://api.telegram.org/bot{token}/sendMessage"
payload = {
    "chat_id": chat_id,
    "text": "✅ SECRET INJECTION TEST"
}

r = requests.post(url, data=payload)
print("STATUS:", r.status_code)
print("RESPONSE:", r.text)

