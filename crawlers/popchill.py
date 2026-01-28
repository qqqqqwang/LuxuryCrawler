from .base import Crawler
from playwright.sync_api import sync_playwright

class PopChillCrawler(Crawler):
    def get_new_items(self):
        url = "https://www.popchill.com/zh-TW/new_products"
        items = []
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url)
                try:
                    page.wait_for_selector('a[href^="/zh-TW/product/"]', timeout=30000)
                except:
                    print("Timeout waiting for PopChill products")
                    browser.close()
                    return []
                    
                cards = page.query_selector_all('a[href^="/zh-TW/product/"]')
                for card in cards[:20]:
                    try:
                        title_el = card.query_selector('div.line-clamp-2')
                        price_el = card.query_selector('div.font-bold')
                        link = card.get_attribute("href")
                        
                        if title_el and price_el and link:
                            title = title_el.inner_text()
                            price = price_el.inner_text()
                            if not link.startswith("http"):
                                link = "https://www.popchill.com" + link
                                
                            items.append({
                                "id": link,
                                "title": title,
                                "price": price,
                                "link": link,
                                "source": "PopChill"
                            })
                    except:
                        pass
                browser.close()
        except Exception as e:
            print(f"Error in PopChillCrawler: {e}")
        return items
