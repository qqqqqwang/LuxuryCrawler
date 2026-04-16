from .base import Crawler
from playwright.sync_api import sync_playwright
from config import URL_ECORING

class EcoRingCrawler(Crawler):
    def get_new_items(self):
        items = []
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--no-sandbox',
                        '--disable-setuid-sandbox'
                    ]
                )
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
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
                print("[EcoRing] Navigating and waiting for /query API callback...")
                
                def handle_response(response):
                    if "query" in response.url.lower():
                        try:
                            js = response.json()
                            if 'list' in js and isinstance(js['list'], list):
                                products = js['list']
                                print(f"[EcoRing] Found 'list' with {len(products)} items in {response.url}")
                                
                                for p in products:
                                    barcode = p.get('barcode')
                                    title = p.get('title')
                                    price = p.get('price')
                                    
                                    if title and barcode:
                                        link = f"https://shop.eco-ring.com.tw/catalogue?search={barcode}"
                                        
                                        # Convert numeric price or clean it up
                                        formatted_price = str(price).split('.')[0] if price else "0"
                                        
                                        items.append({
                                            "id": str(barcode),
                                            "title": title.strip(),
                                            "price": f"NT$ {formatted_price}",
                                            "link": link,
                                            "source": "EcoRing"
                                        })
                        except Exception as e:
                            print(f"[EcoRing] JSON parsing error for {response.url}: {e}")

                page.on("response", handle_response)
                page.goto(URL_ECORING, wait_until="networkidle")
                
                # Fallback wait to make sure API fires and resolves
                page.wait_for_timeout(5000)
                
                print(f"[EcoRing] Intercepted {len(items)} products from the API.")
                browser.close()
                
        except Exception as e:
            print(f"Error in EcoRingCrawler: {e}")
            
        return items
