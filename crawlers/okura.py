import requests
from bs4 import BeautifulSoup
from .base import Crawler
from config import URL_OKURA

class OkuraCrawler(Crawler):
    def get_new_items(self):
        items = []
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            # Fetch the first two pages to ensure we get a good baseline
            for page in range(1, 3):
                url = f"{URL_OKURA}&page={page}" if page > 1 else URL_OKURA
                r = requests.get(url, headers=headers, timeout=15)
                
                if r.status_code != 200:
                    print(f"[OKURA] Failed to fetch page {page}, status code: {r.status_code}")
                    continue
                    
                soup = BeautifulSoup(r.text, 'html.parser')
                cards = soup.select('.xo-product-card')
                
                print(f"[OKURA] Page {page}: Found {len(cards)} items.")
                
                for card in cards:
                    try:
                        title_el = card.select_one('.xo-product-card__title')
                        link_el = card.select_one('a')
                        
                        if not title_el or not link_el:
                            continue
                            
                        title = title_el.text.strip()
                        href = link_el.get('href')
                        
                        # Fix up the link if it's relative
                        if not href.startswith('http'):
                            link = f"https://taiwan.wb-ookura.com{href}"
                        else:
                            link = href
                            
                        # Extract price from all text chunks inside the card
                        texts = [t.strip() for t in card.text.split('\n') if t.strip()]
                        price = "0 TWD"
                        for text in texts:
                            if 'TWD' in text or 'NT$' in text or '$' in text:
                                price = text
                                break
                                
                        items.append({
                            "id": link,
                            "title": title,
                            "price": price,
                            "link": link,
                            "source": "OKURA"
                        })
                    except Exception as e:
                        pass
        except Exception as e:
            print(f"Error in OkuraCrawler: {e}")
            
        return items
