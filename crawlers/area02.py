from .base import Crawler
from playwright.sync_api import sync_playwright
import time
from config import URL_AREA02

class Area02Crawler(Crawler):
    def get_new_items(self):
        items = []
        try:
            # Fixing UA to Desktop Chrome
            user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            
            with sync_playwright() as p:
                # Launch with args to hide automation
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--no-sandbox',
                        '--disable-setuid-sandbox'
                    ]
                )
                context = browser.new_context(
                    user_agent=user_agent,
                    locale="zh-TW",
                    timezone_id="Asia/Taipei",
                    viewport={'width': 1920, 'height': 1080}
                )
                
                # Add stealth script
                context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                """)
                
                page = context.new_page()
                print(f"DEBUG: Navigating to Area02...")
                
                page.goto(URL_AREA02)
                
                # Area02 loads data dynamically, wait for a fixed amount of time for initial cards to render
                page.wait_for_timeout(8000)
                
                # Scroll once down to ensure enough items load
                page.mouse.wheel(0, 3000)
                page.wait_for_timeout(3000)
                
                # Extract items
                try:
                    # Select all a tags since products may not have distinct class selectors initially
                    cards = page.query_selector_all('a')
                    print(f"[Area02] Found {len(cards)} total links. Filtering products...")
                    
                    found_count = 0
                    for card in cards:
                        try:
                            href = card.get_attribute("href")
                            inner_text = card.inner_text().strip()
                            
                            # Valid product links will contain numeric parts or format like Louis Vuttion
                            if href and ('area02.com' in href or href.startswith('/')) and '\n' in inner_text and ('$' in inner_text or 'NT' in inner_text or any(char.isdigit() for char in inner_text)):
                                # Parse title and price from inner text
                                # Usually formatted as: 
                                # 二手 
                                # BRAND / NAME
                                # NT$ 13,850 +
                                
                                lines = [line.strip() for line in inner_text.split('\n') if line.strip()]
                                
                                if len(lines) >= 2:
                                    # Filter out "二手" or "全新" on line 0
                                    title = lines[0]
                                    if "二手" in title or "全新" in title:
                                        title = lines[1] if len(lines) > 1 else lines[0]
                                    
                                    # Find the price line
                                    price = "NT$ 0"
                                    for line in reversed(lines):
                                        if 'NT$' in line or '$' in line or (any(c.isdigit() for c in line) and ',' in line):
                                            price = line.replace('+', '').strip()
                                            break
                                            
                                    link = href
                                    if not link.startswith("http"):
                                        link = "https://www.area02.com" + link
                                        
                                    items.append({
                                        "id": link,
                                        "title": title,
                                        "price": price,
                                        "link": link,
                                        "source": "Area02"
                                    })
                                    found_count += 1
                                    
                                    if found_count >= 100:  # Restrict to ~100 items per run at most
                                        break
                        except Exception as inner_e:
                            pass
                            
                except Exception as e:
                    print(f"Error parsing Area02 items: {e}")
                
                browser.close()
        except Exception as e:
            print(f"Error in Area02Crawler: {e}")
            
        return items
