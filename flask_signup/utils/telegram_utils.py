import requests
import os

from dotenv import load_dotenv
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

print(f"Loaded TELEGRAM_BOT_TOKEN: {TELEGRAM_BOT_TOKEN}")
print(f"Loaded TELEGRAM_CHAT_ID: {TELEGRAM_CHAT_ID}")

def send_telegram_message(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram credentials not set.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }

    try:
        response = requests.post(url, data=data)
        print("Telegram API response status:", response.status_code)
        print("Response content:", response.text)
        response.raise_for_status()
        print("✅ Telegram message sent successfully")
    except Exception as e:
        print(f"❌ Telegram message failed: {e}")
