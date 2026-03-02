from .base import Crawler
from playwright.sync_api import sync_playwright
from config import SECOND_STREET_BRANDS

class SecondStreetCrawler(Crawler):
    def get_new_items(self):
        items = []
        try:
            with sync_playwright() as p:
                # Add stealth and sandbox arguments for Linux environments
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--no-sandbox',
                        '--disable-setuid-sandbox'
                    ]
                )
                # Force Taiwan locale to ensure TWD currency
                context = browser.new_context(
                    locale="zh-TW",
                    timezone_id="Asia/Taipei",
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
                
                # Add stealth script
                context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                """)
                page = context.new_page()
                
                for brand_name, url in SECOND_STREET_BRANDS.items():
                    print(f"Crawling 2ndStreet {brand_name}...")
                    try:
                        page.goto(url)
                        try:
                            page.wait_for_selector(".product-card__vertical", timeout=15000)
                        except:
                            print(f"No items or timeout for 2ndStreet {brand_name}")
                            continue
                        
                        cards = page.query_selector_all(".product-card__vertical")
                        for card in cards[:100]: # Top 100 new items per brand
                            try:
                                title_el = card.query_selector('[data-qe-id="body-meta-field-text"]')
                                price_el = card.query_selector('[data-qe-id="body-price-text"]')
                                link = card.get_attribute("href")
                                
                                if title_el and price_el and link:
                                    title = title_el.inner_text()
                                    price = price_el.inner_text()
                                    if not link.startswith("http"):
                                        link = "https://store.2ndstreet.com.tw" + link
                                    
                                    items.append({
                                        "id": link,
                                        "title": title,
                                        "price": price,
                                        "link": link,
                                        "source": "2ndStreet",
                                        "brand": brand_name
                                    })
                            except Exception as e:
                                print(f"Error parsing 2ndStreet card: {e}")
                    except Exception as e:
                        print(f"Error iterating {brand_name}: {e}")
                
                browser.close()
        except Exception as e:
            print(f"Error in SecondStreetCrawler: {e}")
            
        return items
