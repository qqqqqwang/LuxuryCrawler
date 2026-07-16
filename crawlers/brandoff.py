import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from crawlers.base import Crawler
from config import URL_BRANDOFF_NEW

class BrandOffCrawler(Crawler):
    def get_new_items(self):
        items = []
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            response = requests.get(URL_BRANDOFF_NEW, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            product_elements = soup.select('li > ul')
            
            seen_links = set()
            for ul in product_elements:
                name_el = ul.select_one('.name a')
                if not name_el:
                    continue
                
                title = name_el.text.strip()
                link = name_el.get('href')
                if not link:
                    continue
                    
                link = urljoin("https://tokyotw.brandoff.tw", link)
                    
                if link in seen_links:
                    continue
                seen_links.add(link)
                
                price_el = ul.select_one('.price')
                # Sometimes price has newline (e.g. NT$29,800\nNT$27,800)
                if price_el:
                    price_text = price_el.text.strip()
                    # Split by newline and take the last one (which is usually the sale price if there are two)
                    price_parts = price_text.split()
                    price = price_parts[-1] if price_parts else "0"
                else:
                    price = "0"
                    
                brand_el = ul.select_one('.brand a')
                brand = brand_el.text.strip() if brand_el else None
                
                items.append({
                    "id": link,
                    "title": title,
                    "price": price,
                    "link": link,
                    "source": "BrandOff",
                    "brand": brand
                })
                
            return items
            
        except Exception as e:
            print(f"Error in BrandOffCrawler: {e}")
            return items
