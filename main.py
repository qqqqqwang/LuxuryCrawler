import time
import json
import os
import sys
import logging
from datetime import datetime
from config import DATA_FILE, EXCLUDED_KEYWORDS, SECOND_STREET_BRANDS, URL_POPCHILL, URL_AREA02, URL_OKURA, URL_ECORING, URL_FUGETSU, TARGET_LIST_URL, SWEET_SPOT_TG_CHAT_ID
from crawlers.second_street import SecondStreetCrawler
from crawlers.popchill import PopChillCrawler, PopChillPriceDropCrawler
from crawlers.hermes import HermesCrawler
from crawlers.area02 import Area02Crawler
from crawlers.okura import OkuraCrawler
from crawlers.ecoring import EcoRingCrawler
from crawlers.fugetsu import FugetsuCrawler
from notifier import send_message, notify_sweet_spot
from sweet_spot import SweetSpotMatcher

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

def load_seen_items():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                seen_list = json.load(f)
                migrated = set()
                for item in seen_list:
                    # Migrate old EcoRing barcodes (pure numbers) to ecoring_ prefix
                    if str(item).isdigit():
                        migrated.add(f"ecoring_{item}")
                    else:
                        migrated.add(item)
                return migrated
        except:
            return set()
    return set()

def save_seen_items(seen):
    with open(DATA_FILE, 'w') as f:
        json.dump(list(seen), f)

def job():
    print(f"[{datetime.now()}] Starting scan...")
    seen = load_seen_items()
    is_first_run = len(seen) == 0
    
    if is_first_run:
        print("First run detected. Establishing baseline (no notifications)...")

    # Load sweet spot matcher
    sweet_spot_matcher = SweetSpotMatcher(TARGET_LIST_URL)

    # Define crawlers with their listing URLs for the footer link
    crawlers_config = [
        (SecondStreetCrawler(), None, "2ndstreet"),
        (PopChillCrawler(), URL_POPCHILL, "popchill"),
        (PopChillPriceDropCrawler(), "https://www.popchill.com/zh-TW/price_drop_products", "popchill_drop"),
        (HermesCrawler(), None, "hermes"),
        (Area02Crawler(), URL_AREA02, "area02"),
        (OkuraCrawler(), URL_OKURA, "okura"),
        (EcoRingCrawler(), URL_ECORING, "ecoring"),
        (FugetsuCrawler(), URL_FUGETSU, "fugetsu")
    ]
    
    new_items_total = 0
    
    for crawler, listing_url, url_keyword in crawlers_config:
        crawler_name = type(crawler).__name__.replace("Crawler", "")
        
        # Check if we have history for this specific source
        has_history = any(url_keyword in item_id for item_id in seen)
        
        try:
            print(f"Running {crawler_name} (History: {has_history})...")
            items = crawler.get_new_items()
            print(f"Found {len(items)} items on {crawler_name}")
            
            # Log crawled items for debugging (User Request)
            for i, item in enumerate(items):
                print(f"  [{i+1}] {item['title']} | {item['price']} | ID: {item['id'][-15:]}...")
            
            
            new_items_batch = []
            for item in items:
                if item['id'] not in seen:
                    # Check for excluded keywords (Brand Filter)
                    is_excluded = False
                    for keyword in EXCLUDED_KEYWORDS:
                        if keyword.lower() in item['title'].lower():
                            print(f"  -> Filtered out: {item['title']} (Matched '{keyword}')")
                            is_excluded = True
                            break
                    
                    if not is_excluded:
                        new_items_batch.append(item)
                    
                    # Mark as seen regardless to avoid re-processing
                    seen.add(item['id'])
            
            if new_items_batch:
                print(f"Found {len(new_items_batch)} NEW items on {crawler_name}")
                
                # Sweet Spot check (Independent mechanism - Wrapped in try-except for Absolute Defense)
                for item in new_items_batch:
                    try:
                        try:
                            price_str = str(item.get('price', '0'))
                            price_clean = price_str.replace("NT$", "").replace("TWD", "").replace("$", "").replace(",", "").strip()
                            price_int = int(price_clean)
                        except (ValueError, TypeError):
                            price_int = 0
                            
                        is_sweet, is_high, target_info = sweet_spot_matcher.check_item(
                            item_brand=item.get('brand', ''),
                            item_title=item.get('title', ''),
                            item_price=price_int
                        )
                        
                        if is_sweet:
                            print(f"  *** 🚨 甜漏價命中! [{target_info.get('品牌')}] {item['title']}")
                            notify_sweet_spot(item, is_high, target_info)
                    except Exception as e:
                        print(f"  [SweetSpot Error] Critical defensive skip: {e}")
                        # Even if sweet spot fails, we continue the loop for other items 
                        # and let standard notifications proceed.
                        continue
                
                # Notification Logic:
                # 1. If global seen is completely empty -> First Run (Baseline)
                if len(seen) - len(new_items_batch) == 0:
                     print(f"Skipping notification for {crawler_name} (Global First Run)")
                
                # Special handling for 2ndStreet (Brand-specific notifications)
                elif crawler_name == "SecondStreet":
                    if not has_history:
                        print("Skipping notification for 2ndStreet (New Source Baseline)")
                    else:
                        # Group by brand
                        brand_items = {}
                        for item in new_items_batch:
                            brand = item.get("brand", "Unknown")
                            if brand not in brand_items:
                                brand_items[brand] = []
                            brand_items[brand].append(item)
                            
                        if brand_items:
                            brands_list = ", ".join(brand_items.keys())
                            msg = f"<b>2nd street 新品上架：{brands_list}</b>\n"
                            msg += "─────\n"
                            for brand, items in brand_items.items():
                                brand_url = SECOND_STREET_BRANDS.get(brand, "")
                                msg += f"✨ <b>{brand}</b> ({len(items)}件) 👉 <a href='{brand_url}'>查看頁面</a>\n\n"
                                
                            send_message(msg.strip())
                
                # Handling for Hermes (Category-specific notifications)
                elif crawler_name == "Hermes":
                    # Group by category (Bags vs Small Leather Goods)
                    category_items = {}
                    for item in new_items_batch:
                        cat = item.get("category", "Unknown")
                        if cat not in category_items:
                            category_items[cat] = []
                        category_items[cat].append(item)
                        
                    for cat, items in category_items.items():
                        if not has_history:
                            print(f"Skipping notification for Hermes {cat} (New Source Baseline)")
                            continue
                            
                        msg = f"<b>Hermes 愛馬仕 {cat} 官網有新品上架了！({len(items)}件)</b>\n\n"
                        
                        for item in items[:10]:
                            msg += f"• {item['title']} 👉 <a href='{item['link']}'>前往商品</a>\n\n"
                            
                        if len(items) > 10:
                            msg += f"...and {len(items) - 10} more.\n"
                    
                        send_message(msg)
                
                # Handling for PopChill Price Drop (Special channel notification)
                elif crawler_name == "PopChillPriceDrop":
                    if not has_history:
                        print(f"Skipping notification for {crawler_name} (New Source Baseline)")
                    else:
                        msg = f"📉 <b>拍拍圈降價：發現 {len(new_items_batch)} 個降價商品</b>\n\n"
                        
                        for item in new_items_batch[:10]:
                            price_display = item['price'].replace("NT$", "").replace("TWD", "").replace("$", "").strip()
                            msg += f"• {item['title']} 【TWD {price_display}】 👉 <a href='{item['link']}'>前往商品</a>\n\n"
                        
                        if len(new_items_batch) > 10:
                            msg += f"...and {len(new_items_batch) - 10} more.\n"
                            
                        msg += f"\n<a href='{listing_url}'>查看所有降價商品</a>"
                        
                        if SWEET_SPOT_TG_CHAT_ID:
                            send_message(msg, chat_ids=[SWEET_SPOT_TG_CHAT_ID])
                        else:
                            print("No SWEET_SPOT_TG_CHAT_ID found. Falling back to default.")
                            send_message(msg)
                
                # Handling for PopChill (General notifications)
                else:
                    if not has_history:
                         print(f"Skipping notification for {crawler_name} (New Source Baseline)")
                    else:
                        display_name = crawler_name
                        if crawler_name.lower() == "popchill":
                            display_name = "拍拍圈"
                        elif crawler_name.lower() == "area02":
                            display_name = "Area02"
                        elif crawler_name.lower() == "okura":
                            display_name = "OKURA"
                        elif crawler_name.lower() == "ecoring":
                            display_name = "EcoRing"
                        elif crawler_name.lower() == "fugetsu":
                            display_name = "楓月"
                            
                        msg = f"<b>{display_name} 新品上架：{len(new_items_batch)} 商品</b>\n\n"
                        
                        for item in new_items_batch[:10]:
                            price_display = item['price'].replace("NT$", "").replace("TWD", "").replace("$", "").strip()
                            msg += f"• {item['title']} 【TWD {price_display}】 👉 <a href='{item['link']}'>前往商品</a>\n\n"
                        
                        if len(new_items_batch) > 10:
                            msg += f"...and {len(new_items_batch) - 10} more.\n"
                            
                        msg += f"\n<a href='{listing_url}'>View All New Items</a>"
                        
                        send_message(msg)
                    
                new_items_total += len(new_items_batch)
            else:
                print(f"No new items on {crawler_name}")

        except Exception as e:
            print(f"Error in crawler {crawler_name}: {e}")
            
    save_seen_items(seen)
    print(f"[{datetime.now()}] Scan complete. Found {new_items_total} new items.")

def main():
    print("Luxury Crawler Execution Started...")
    try:
        job()
        print("Done.")
    except Exception as e:
        print(f"Fatal Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
