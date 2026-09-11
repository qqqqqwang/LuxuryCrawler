import requests
import json
from config import (
    DISCORD_WEBHOOK_2NDSTREET,
    DISCORD_WEBHOOK_POPCHILL,
    DISCORD_WEBHOOK_POPCHILL_DROP,
    DISCORD_WEBHOOK_ECORING,
    DISCORD_WEBHOOK_OTHERS,
    SECOND_STREET_BRANDS
)

BRAND_COLORS = {
    "CHANEL": 0,           # Black (0x000000)
    "LOUIS VUITTON": 9070381,  # Brown (0x8A5A44)
    "LV": 9070381,         
    "HERMES": 16738048,    # Hermes Orange (0xFF6600)
    "DIOR": 12632256,      # Silver/Grey (0xC0C0C0)
    "GUCCI": 11469824,     # Gucci Red (0xAF0000)
    "PRADA": 128,          # Navy Blue (0x000080)
    "CELINE": 8388608,     # Burgundy (0x800000)
    "GOYARD": 16766720,    # Bright Yellow (0xFFD700)
    "SAINT LAURENT": 7829367, # Dark Grey (0x777777)
    "YSL": 7829367,        # Dark Grey (0x777777)
    "FENDI": 14329120,     # Mustard/Gold (0xDAA520)
    "LOEWE": 12558434,     # Tan/Beige (0xBFA162)
    "BVLGARI": 8388736,    # Purple (0x800080)
    "BOTTEGA VENETA": 32768, # BV Green (0x008000)
    "THE ROW": 3100495,    # Dark Slate (0x2F4F4F)
    "BURBERRY": 14404531,  # Burberry Plaid Beige (0xDBBCA3)
    "VIVIENNE WESTWOOD": 13369344, # Westwood Red (0xCC0000)
    "BALENCIAGA": 3426654, # Dark Blue/Grey (0x34495E)
    "MIU MIU": 16758465,   # Light Pink (0xFFB6C1)
    "ISSEY MIYAKE": 11184810, # Light Grey (0xAAAAAA)
    "MONCLER": 16711680,   # Pure Red (0xFF0000)
    "ROGER VIVIER": 14822765, # Magenta (0xE22A6D)
    "ACNE STUDIOS": 16761035, # Acne Pink (0xFFC0CB)
}

def get_brand_color(brand, default_color):
    b_upper = brand.upper()
    for b, c in BRAND_COLORS.items():
        if b in b_upper:
            return c
    return default_color

def send_discord_webhook(webhook_url, payload):
    """
    Sends a payload to a Discord Webhook.
    """
    if not webhook_url:
        return
        
    import time
    
    try:
        response = requests.post(
            webhook_url,
            data=json.dumps(payload),
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        if response.status_code == 429:
            retry_after = response.json().get("retry_after", 1)
            time.sleep(retry_after)
            response = requests.post(
                webhook_url,
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
        if not response.ok:
            print(f"Discord API Error: {response.status_code} - {response.text}")
        response.raise_for_status()
        time.sleep(0.5)  # Rate limit prevention (5 req / 2 sec)
    except Exception as e:
        print(f"Failed to send Discord webhook: {e}")

import re

def format_price(price_str):
    """Clean and format price for display."""
    if isinstance(price_str, str):
        match = re.search(r'[\d,]+(?:\.\d+)?', price_str)
        if match:
            clean_price = match.group().replace(',', '')
            try:
                if '.' in clean_price:
                    return f"{float(clean_price):,.2f}"
                else:
                    return f"{int(clean_price):,}"
            except:
                pass
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

    embeds = []
    
    # 1. Overview Card
    overview_embed = {
        "title": "📋 2nd Street | 本次新品上架總覽",
        "color": 3447003,
        "fields": []
    }
    for brand, items in brand_items.items():
        overview_embed["fields"].append({
            "name": brand,
            "value": f"共 {len(items)} 件",
            "inline": True
        })
    # Only add overview if there's actually something to show
    if overview_embed["fields"]:
        embeds.append(overview_embed)
    
    # 2. Individual Item Cards
    for brand, items in brand_items.items():
        brand_url = SECOND_STREET_BRANDS.get(brand, "")
        brand_color = get_brand_color(brand, 3447003)
        
        for i, item in enumerate(items[:10]):
            title = item.get('title')
            if not title:
                title = '商品名稱未定'
            title = title[:256]
            price = format_price(item.get('price', '0'))
            link = item.get('link', '')
            image_url = item.get('image', '')
            
            embed = {
                "title": title[:256],
                "url": link,
                "color": brand_color,
                "author": {
                    "name": f"✨ 2nd Street | {brand} (共 {len(items)} 件)",
                    "url": brand_url if brand_url else link,
                },
                "fields": [
                    {
                        "name": "💰 售價 (Price)",
                        "value": f"**TWD {price}**",
                        "inline": True
                    },
                    {
                        "name": "🏷️ 品牌 (Brand)",
                        "value": brand,
                        "inline": True
                    }
                ]
            }
            
            if image_url:
                embed["thumbnail"] = {"url": image_url}
                
            # If this is the 10th item and there are more, add a footer note
            if i == 9 and len(items) > 10:
                embed["footer"] = {"text": f"還有 {len(items) - 10} 件 {brand} 商品未顯示，請點擊上方標題回原網站查看..."}
                
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
    
    if crawler_name.lower() == "popchill":
        webhook_url = DISCORD_WEBHOOK_POPCHILL
        display_name = "拍拍圈"
        color = 15277667  # Pink
    elif crawler_name.lower() == "popchillpricedrop":
        webhook_url = DISCORD_WEBHOOK_POPCHILL_DROP
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
    
    # 1. Overview Card
    overview_embed = {
        "title": f"📋 {display_name} | {title_prefix}總覽",
        "color": color,
        "fields": []
    }
    for brand, b_items in brand_items.items():
        overview_embed["fields"].append({
            "name": brand,
            "value": f"共 {len(b_items)} 件",
            "inline": True
        })
    if overview_embed["fields"]:
        embeds.append(overview_embed)
    
    # 2. Individual Item Cards
    for brand, b_items in brand_items.items():
        brand_color = get_brand_color(brand, color)
        
        for i, item in enumerate(b_items[:10]):
            title = item.get('title')
            if not title:
                title = '商品名稱未定'
            title = title[:256]
            price = format_price(item.get('price', '0'))
            link = item.get('link', '')
            image_url = item.get('image', '')
            
            author_name = f"{title_prefix} | {display_name}"
            if brand != "未分類":
                author_name += f" | {brand}"
            author_name += f" (共 {len(b_items)} 件)"
                
            embed = {
                "title": title[:256],
                "url": link,
                "color": brand_color,
                "author": {
                    "name": author_name,
                    "url": listing_url if listing_url else link,
                },
                "fields": [
                    {
                        "name": "💰 售價 (Price)",
                        "value": f"**TWD {price}**",
                        "inline": True
                    }
                ]
            }
            
            if brand != "未分類":
                embed["fields"].append({
                    "name": "🏷️ 品牌 (Brand)",
                    "value": brand,
                    "inline": True
                })
                
            if image_url:
                embed["thumbnail"] = {"url": image_url}
                
            if i == 9 and len(b_items) > 10:
                embed["footer"] = {"text": f"還有 {len(b_items) - 10} 件商品未顯示，請點擊上方標題回原網站查看..."}
                
            embeds.append(embed)
            
            if len(embeds) == 10:
                send_discord_webhook(webhook_url, {"embeds": embeds})
                embeds = []
            
    if embeds:
        send_discord_webhook(webhook_url, {"embeds": embeds})
