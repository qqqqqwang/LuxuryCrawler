from .base import Crawler
from playwright.sync_api import sync_playwright

class SecondStreetCrawler(Crawler):
    def get_new_items(self):
        url = "https://store.2ndstreet.com.tw/v2/official/SalePageCategory/442462?sortMode=Newest"
        items = []
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                # Force Taiwan locale to ensure TWD currency
                context = browser.new_context(
                    locale="zh-TW",
                    timezone_id="Asia/Taipei",
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
                page = context.new_page()
                page.goto(url)
                try:
                    page.wait_for_selector(".product-card__vertical", timeout=30000)
                except:
                    print("Timeout waiting for 2ndStreet products")
                    browser.close()
                    return []
                
                cards = page.query_selector_all(".product-card__vertical")
                for card in cards[:50]: # Check top 50 to be safe
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
                                "source": "2ndStreet"
                            })
                    except Exception as e:
                        print(f"Error parsing 2ndStreet card: {e}")
                browser.close()
        except Exception as e:
            print(f"Error in SecondStreetCrawler: {e}")
            
        return items
