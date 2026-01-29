from .base import Crawler
from playwright.sync_api import sync_playwright
import time
from fake_useragent import UserAgent

class PopChillCrawler(Crawler):
    def get_new_items(self):
        url = "https://www.popchill.com/zh-TW/new_products"
        items = []
        try:
            ua = UserAgent()
            user_agent = ua.random
            
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
                print(f"DEBUG: Navigating to {url} with UA {user_agent}...")
                page.goto(url, wait_until="networkidle") # Wait for network to settle
                
                # Wait longer and try to identify why it fails
                try:
                    page.wait_for_selector('a[href^="/zh-TW/product/"]', timeout=45000)
                except Exception as e:
                    print(f"DEBUG: Timeout on PopChill. Content preview: {page.content()[:500]}")
                    page.screenshot(path="popchill_debug.png")
                    browser.close()
                    return []
                
                # Scroll down to load more items (Lazy Loading)
                for _ in range(3): 
                    page.mouse.wheel(0, 3000)
                    page.wait_for_timeout(1500)
                    
                cards = page.query_selector_all('a[href^="/zh-TW/product/"]')
                for card in cards[:50]:
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
