import time
import json
import os
import sys
from datetime import datetime
from config import DATA_FILE
from crawlers.second_street import SecondStreetCrawler
from crawlers.popchill import PopChillCrawler
from notifier import send_message

def load_seen_items():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return set(json.load(f))
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

    # Define crawlers with their listing URLs for the footer link
    crawlers_config = [
        (SecondStreetCrawler(), "https://store.2ndstreet.com.tw/v2/official/SalePageCategory/442462?sortMode=Newest", "2ndstreet"),
        (PopChillCrawler(), "https://www.popchill.com/zh-TW/new_products", "popchill")
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
            
            new_items_batch = []
            for item in items:
                if item['id'] not in seen:
                    new_items_batch.append(item)
                    seen.add(item['id'])
            
            if new_items_batch:
                print(f"Found {len(new_items_batch)} NEW items on {crawler_name}")
                
                # Notification Logic:
                # 1. If global seen is completely empty -> First Run (Baseline)
                # 2. If this specific source has NO history -> New Source (Baseline)
                if len(seen) - len(new_items_batch) == 0: # Was empty before this batch
                     print(f"Skipping notification for {crawler_name} (Global First Run)")
                elif not has_history:
                     print(f"Skipping notification for {crawler_name} (New Source Baseline)")
                else:
                    # Not first run, and has history -> Genuine new items
                    msg = f"<b>{len(new_items_batch)} New Items on {crawler_name}!</b>\n\n"
                    
                    for item in new_items_batch[:10]:
                        msg += f"• {item['title']} ({item['price']})\n"
                    
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
