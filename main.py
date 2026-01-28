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
    crawlers = [SecondStreetCrawler(), PopChillCrawler()]
    new_items_count = 0
    
    for crawler in crawlers:
        try:
            print(f"Running {type(crawler).__name__}...")
            items = crawler.get_new_items()
            print(f"Found {len(items)} items on {type(crawler).__name__}")
            
            for item in items:
                if item['id'] not in seen:
                    # New item!
                    msg = (
                        f"<b>New Item on {item['source']}!</b>\n\n"
                        f"{item['title']}\n"
                        f"Price: {item['price']}\n"
                        f"<a href='{item['link']}'>View Product</a>"
                    )
                    print(f"Sending notification for: {item['title']}")
                    send_message(msg)
                    seen.add(item['id'])
                    new_items_count += 1
                    time.sleep(2) # Avoid rate limits
        except Exception as e:
            print(f"Error in crawler {type(crawler).__name__}: {e}")
            
    save_seen_items(seen)
    print(f"[{datetime.now()}] Scan complete. Found {new_items_count} new items.")

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
