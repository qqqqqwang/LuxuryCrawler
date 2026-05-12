import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .base import Crawler
from config import URL_FUGETSU

class FugetsuCrawler(Crawler):
    def get_new_items(self):
        items = []
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            # Fetch the first two pages to ensure we get a good baseline
            for page in range(1, 3):
                url = f"{URL_FUGETSU}&pno={page}"
                r = requests.get(url, headers=headers, timeout=15)
                
                if r.status_code != 200:
                    print(f"[Fugetsu] Failed to fetch page {page}, status code: {r.status_code}")
                    continue
                    
                soup = BeautifulSoup(r.text, 'html.parser')
                cards = soup.select('.main-product')
                
                print(f"[Fugetsu] Page {page}: Found {len(cards)} items.")
                
                for card in cards:
                    try:
                        title_el = card.select_one('a.product-title')
                        price_el = card.select_one('span.amount')
                        
                        if not title_el or not price_el:
                            continue
                            
                        title = title_el.text.strip()
                        href = title_el.get('href')
                        
                        # Fix up the link if it's relative
                        link = urljoin("https://brandfugetsu.com", href)
                            
                        price = price_el.text.strip()
                                
                        items.append({
                            "id": link,
                            "title": title,
                            "price": price,
                            "link": link,
                            "source": "楓月"
                        })
                    except Exception as e:
                        pass
        except Exception as e:
            print(f"Error in FugetsuCrawler: {e}")
            
        return items
