import requests
import json
import random
import time
import re

from config import (
    DISCORD_WEBHOOK_2NDSTREET,
    DISCORD_WEBHOOK_POPCHILL,
    DISCORD_WEBHOOK_POPCHILL_DROP,
    DISCORD_WEBHOOK_ECORING,
    DISCORD_WEBHOOK_OTHERS,
    SECOND_STREET_BRANDS
)

BATCH_COLORS = [
    3447003,   # Blue
    15277667,  # Pink
    16738048,  # Orange
    1636259,   # Green
    10824234,  # Purple
    16766720,  # Yellow
    11469824,  # Red
    8388608,   # Burgundy
    3100495,   # Slate
    32768,     # BV Green
    14404531,  # Beige
    3426654,   # Dark Blue
]

# Single random color for the entire lifecycle of this script run
RUN_COLOR = random.choice(BATCH_COLORS)

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
    if not DISCORD_WEBHOOK_2NDSTREET:
        return

    embeds = []
    
    # 1. Overview Card (uses description for markdown links)
    desc_lines = []
    for brand, items in brand_items.items():
        brand_url = SECOND_STREET_BRANDS.get(brand, "")
        if brand_url:
            desc_lines.append(f"**[{brand}]({brand_url})**: {len(items)} 件")
        else:
            desc_lines.append(f"**{brand}**: {len(items)} 件")
            
    overview_embed = {
        "title": "📋 2nd Street | 本次新品上架總覽",
        "color": RUN_COLOR,
        "description": "\\n".join(desc_lines)
    }
    
    if desc_lines:
        embeds.append(overview_embed)
    
    # 2. Individual Item Cards
    for brand, items in brand_items.items():
        brand_url = SECOND_STREET_BRANDS.get(brand, "")
        
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
                "color": RUN_COLOR,
                "author": {
                    "name": f"✨ 2nd Street | {brand} (共 {len(items)} 件)",
                    "url": brand_url if brand_url else link,
                },
                "fields": [
                    {
                        "name": "💰 售價 (Price)",
                        "value": f"**TWD {price}**",
                        "inline": True
                    }
                ]
            }
            
            if image_url:
                embed["thumbnail"] = {"url": image_url}
                
            embed["footer"] = {"text": f"📍 {brand} ( {i+1} / {len(items)} ) ｜ 點擊上方標題看更多 👆"}
                
            embeds.append(embed)
            
            if len(embeds) == 10:
                send_discord_webhook(DISCORD_WEBHOOK_2NDSTREET, {"embeds": embeds})
                embeds = []
            
    if embeds:
        send_discord_webhook(DISCORD_WEBHOOK_2NDSTREET, {"embeds": embeds})


def notify_platform_discord(crawler_name, items, listing_url, is_price_drop=False):
    webhook_url = DISCORD_WEBHOOK_OTHERS
    display_name = crawler_name
    
    if crawler_name.lower() == "popchill":
        webhook_url = DISCORD_WEBHOOK_POPCHILL
        display_name = "拍拍圈"
    elif crawler_name.lower() == "popchillpricedrop":
        webhook_url = DISCORD_WEBHOOK_POPCHILL_DROP
        display_name = "拍拍圈"
    elif crawler_name.lower() == "ecoring":
        webhook_url = DISCORD_WEBHOOK_ECORING
        display_name = "EcoRing"

    if not webhook_url:
        return

    embeds = []
    title_prefix = "📉 降價通知" if is_price_drop else "✨ 新品上架"
    
    for i, item in enumerate(items[:10]):
        title = item.get('title')
        if not title:
            title = '商品名稱未定'
        title = title[:256]
        price = format_price(item.get('price', '0'))
        link = item.get('link', '')
        image_url = item.get('image', '')
        
        author_name = f"{title_prefix} | {display_name} (共 {len(items)} 件)"
            
        embed = {
            "title": title[:256],
            "url": link,
            "color": RUN_COLOR,
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
        
        if image_url:
            embed["thumbnail"] = {"url": image_url}
            
        embed["footer"] = {"text": f"📍 本批上新 ( {i+1} / {len(items)} ) ｜ 點擊上方標題看更多 👆"}
            
        embeds.append(embed)
        
        if len(embeds) == 10:
            send_discord_webhook(webhook_url, {"embeds": embeds})
            embeds = []
        
    if embeds:
        send_discord_webhook(webhook_url, {"embeds": embeds})
