import os
import requests

token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")

print("Token exists:", bool(token))
print("Chat ID:", chat_id)

url = f"https://api.telegram.org/bot{token}/sendMessage"
payload = {
    "chat_id": chat_id,
    "text": "✅ FINAL TELEGRAM TEST — THIS SHOULD APPEAR"
}

r = requests.post(url, data=payload)
print("Status:", r.status_code)
print("Response:", r.text)
