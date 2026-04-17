import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_IDS, SWEET_SPOT_TG_CHAT_ID

def send_message(message, chat_ids=None):
    """
    Sends a message to Telegram.
    If chat_ids is not provided, sends to the default TELEGRAM_CHAT_IDS.
    """
    if chat_ids is None:
        chat_ids = TELEGRAM_CHAT_IDS
        
    if not TELEGRAM_BOT_TOKEN or not chat_ids:
        print("Telegram credentials missing, skipping notification.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    # Ensure chat_ids is a list
    if isinstance(chat_ids, str):
        chat_ids = chat_ids.split(",")
        
    for chat_id in chat_ids:
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

def notify_sweet_spot(item, is_high_confidence, target_info):
    """
    Formats and sends a sweet spot notification to the dedicated sweet spot channel.
    """
    if not SWEET_SPOT_TG_CHAT_ID:
        print("No Sweet Spot chat ID configured, skipping sweet spot notification.")
        return

    if is_high_confidence:
        title = "🔥 <b>【甜漏價_高信心】</b>"
    else:
        title = "👀 <b>【甜漏價_需確認】</b>"
        
    # Clean and convert prices to int for display formatting
    try:
        raw_price = item.get('price', '0')
        if isinstance(raw_price, str):
            clean_price = "".join(filter(str.isdigit, raw_price))
            display_price = int(clean_price)
        else:
            display_price = int(raw_price)
    except:
        display_price = 0
        
    try:
        target_price = int(target_info.get('甜漏價', 0))
    except:
        target_price = 0
        
    lines = [
        f"{title}",
        f"<b>商品：</b><a href='{item.get('link', '')}'>{item.get('title', '無標題')}</a>",
        f"<b>品牌：</b>{target_info.get('品牌', item.get('brand', '未知'))}",
        f"<b>售價：</b>${display_price:,} (目標價: ${target_price:,})"
    ]
    
    missing_info = target_info.get('missing_info', [])
    if missing_info:
        lines.append(f"<b>⚠️ 缺漏/未命中資訊：</b>{', '.join(missing_info)}")
        
    message = "\n".join(lines)
    send_message(message, chat_ids=[SWEET_SPOT_TG_CHAT_ID])
