import os
import requests

print("🚨 TELEGRAM TEST START 🚨")

token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")

print("Token exists:", bool(token))
print("Chat ID exists:", bool(chat_id))

url = f"https://api.telegram.org/bot{token}/sendMessage"
payload = {
    "chat_id": chat_id,
    "text": "🚨 TEST MESSAGE FROM GITHUB ACTION 🚨",
}

r = requests.post(url, data=payload)
print("Status:", r.status_code)
print("Response:", r.text)
