from crawlers.base import Crawler
from playwright.sync_api import sync_playwright
import time
from config import HERMES_URLS

class HermesCrawler(Crawler):
    def get_new_items(self):
        items = []
        
        with sync_playwright() as p:
            # We must use chromium with some stealth arguments to have a chance against anti-bots
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-infobars',
                    '--window-size=1920,1080',
                ]
            )
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={'width': 1920, 'height': 1080}
            )
            
            # Hide webdriver flag
            context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            page = context.new_page()
            
            for category_name, url in HERMES_URLS.items():
                print(f"[{category_name}] Navigating to {url}")
                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    # Wait for items to potentially load or anti-bot challenge
                    page.wait_for_timeout(5000)
                    
                    html = page.content()
                    if "captcha" in html.lower() or "datadome" in html.lower() or "challenge" in html.lower():
                        print(f"[{category_name}] Error: Blocked by Hermes Anti-Bot (DataDome). Skipping...")
                        continue
                    
                    # Scroll down slowly to trigger infinite load
                    print(f"[{category_name}] Scrolling to load products...")
                    last_height = page.evaluate("document.body.scrollHeight")
                    while True:
                        page.keyboard.press("PageDown")
                        page.wait_for_timeout(1000) # Wait for network
                        new_height = page.evaluate("document.body.scrollHeight")
                        if new_height == last_height:
                            break
                        last_height = new_height
                    
                    # Parse the products
                    # User provided HTML: <a class="product-item-name" href="/tw/zh/product/so-medor肩背包-H085054CK37/" title="So Medor肩背包, 米色/原色"><span class="product-title">So Medor肩背包</span></a>
                    product_nodes = page.query_selector_all('a.product-item-name')
                    print(f"[{category_name}] Found {len(product_nodes)} products.")
                    
                    for node in product_nodes:
                        href = node.get_attribute('href')
                        title = node.get_attribute('title')
                        
                        if not href or not title:
                            continue
                            
                        # Extract exact sku from href or use href as id
                        # href example: /tw/zh/product/so-medor肩背包-H085054CK37/
                        item_id = href.strip('/')
                        full_link = f"https://www.hermes.com{href}"
                        
                        # Note: Hermes price is not in the 'a.product-item-name' tag block directly from user snapshot
                        # We will set Price to N/A for now and focus on stock alert
                        price = "N/A"
                        
                        items.append({
                            'id': item_id,
                            'title': title,
                            'link': full_link,
                            'price': price,
                            'brand': 'Hermes',
                            'category': category_name
                        })

                except Exception as e:
                    print(f"[{category_name}] Error crawling Hermes: {e}")
                    
            browser.close()
            
        return items
