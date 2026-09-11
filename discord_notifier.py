import requests
import json
from config import (
    DISCORD_WEBHOOK_2NDSTREET,
    DISCORD_WEBHOOK_POPCHILL,
    DISCORD_WEBHOOK_ECORING,
    DISCORD_WEBHOOK_OTHERS,
    SECOND_STREET_BRANDS
)

def send_discord_webhook(webhook_url, payload):
    """
    Sends a payload to a Discord Webhook.
    """
    if not webhook_url:
        return
        
    try:
        response = requests.post(
            webhook_url,
            data=json.dumps(payload),
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        response.raise_for_status()
    except Exception as e:
        print(f"Failed to send Discord webhook: {e}")

def format_price(price_str):
    """Clean and format price for display."""
    if isinstance(price_str, str):
        clean_price = "".join(filter(str.isdigit, price_str))
        try:
            return f"{int(clean_price):,}"
        except:
            return price_str
    try:
        return f"{int(price_str):,}"
    except:
        return str(price_str)

def notify_2ndstreet_discord(brand_items):
    """
    Sends 2nd Street notifications grouped by brand.
    Uses fields inside an embed for a compact, neat look.
    """
    if not DISCORD_WEBHOOK_2NDSTREET:
        return

    # Discord embeds can have max 25 fields.
    # To be safe, we'll create one embed per brand if it has many items, 
    # or chunk them into multiple embeds.
    
    embeds = []
    
    for brand, items in brand_items.items():
        brand_url = SECOND_STREET_BRANDS.get(brand, "")
        
        embed = {
            "title": f"✨ 2nd Street 新品上架: {brand}",
            "url": brand_url if brand_url else None,
            "color": 3447003,  # Blue color
            "fields": []
        }
        
        # Add up to 25 items per brand (Discord limit for fields is 25)
        for item in items[:25]:
            price = format_price(item.get('price', '0'))
            embed["fields"].append({
                "name": item.get('title', '商品名稱未定')[:256], # Discord name limit
                "value": f"💰 **TWD {price}**\n[👉 前往商品]({item.get('link', '')})",
                "inline": True
            })
            
        if len(items) > 25:
            embed["footer"] = {"text": f"還有 {len(items) - 25} 件商品未顯示..."}
            
        embeds.append(embed)
        
        # Webhook payload can have max 10 embeds. If we exceed, send and reset.
        if len(embeds) == 10:
            send_discord_webhook(DISCORD_WEBHOOK_2NDSTREET, {"embeds": embeds})
            embeds = []
            
    if embeds:
        send_discord_webhook(DISCORD_WEBHOOK_2NDSTREET, {"embeds": embeds})


def notify_platform_discord(crawler_name, items, listing_url, is_price_drop=False):
    """
    Sends notifications for other platforms.
    Routes to POPCHILL, ECORING, or OTHERS webhook based on crawler_name.
    """
    webhook_url = DISCORD_WEBHOOK_OTHERS
    color = 9807270  # Grey default
    display_name = crawler_name
    
    if crawler_name.lower() == "popchill" or crawler_name.lower() == "popchillpricedrop":
        webhook_url = DISCORD_WEBHOOK_POPCHILL
        display_name = "拍拍圈"
        color = 15277667  # Pink
    elif crawler_name.lower() == "ecoring":
        webhook_url = DISCORD_WEBHOOK_ECORING
        display_name = "EcoRing"
        color = 3066993   # Greenish
    elif crawler_name.lower() == "area02":
        display_name = "Area02"
        color = 0         # Black
    elif crawler_name.lower() == "okura":
        display_name = "OKURA"
        color = 10181046  # Purple
    elif crawler_name.lower() == "fugetsu":
        display_name = "楓月"
        color = 15105570  # Orange
    elif crawler_name.lower() == "hermes":
        display_name = "Hermes"
        color = 16738048  # Hermes Orange

    if not webhook_url:
        return

    # Group by brand if possible, otherwise flat list
    brand_items = {}
    for item in items:
        brand = item.get("brand", "未分類")
        if not brand:
            brand = "未分類"
        if brand not in brand_items:
            brand_items[brand] = []
        brand_items[brand].append(item)

    embeds = []
    
    title_prefix = "📉 降價通知" if is_price_drop else "✨ 新品上架"
    
    # Create an embed for each brand
    for brand, b_items in brand_items.items():
        embed_title = f"{title_prefix}: {display_name} - {brand}" if brand != "未分類" else f"{title_prefix}: {display_name}"
        
        embed = {
            "title": embed_title,
            "url": listing_url,
            "color": color,
            "fields": []
        }
        
        for item in b_items[:25]:
            price = format_price(item.get('price', '0'))
            
            # Format the field name (title) and value (price + link)
            title = item.get('title', '商品名稱未定')[:256]
            embed["fields"].append({
                "name": title,
                "value": f"💰 **TWD {price}**\n[👉 前往商品]({item.get('link', '')})",
                "inline": True
            })
            
        if len(b_items) > 25:
            embed["footer"] = {"text": f"還有 {len(b_items) - 25} 件 {brand} 商品未顯示..."}
            
        embeds.append(embed)
        
        if len(embeds) == 10:
            send_discord_webhook(webhook_url, {"embeds": embeds})
            embeds = []
            
    if embeds:
        send_discord_webhook(webhook_url, {"embeds": embeds})
