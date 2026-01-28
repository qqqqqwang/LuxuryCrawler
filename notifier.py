import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_IDS

def send_message(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_IDS:
        print("Telegram credentials missing, skipping notification.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    for chat_id in TELEGRAM_CHAT_IDS:
        chat_id = chat_id.strip()
        if not chat_id:
            continue
            
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML",
            # "disable_web_page_preview": False
        }
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
        except Exception as e:
            print(f"Failed to send message to {chat_id}: {e}")
