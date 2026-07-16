import requests
from bs4 import BeautifulSoup
from crawlers.base import Crawler
from config import URL_TOWERWATCH

class TowerWatchCrawler(Crawler):
    def get_new_items(self):
        items = []
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            response = requests.get(URL_TOWERWATCH, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            product_elements = soup.select(".product-item")
            
            seen_links = set()
            for element in product_elements:
                a_tag = element.select_one("a")
                link = a_tag['href'] if a_tag else ""
                if not link:
                    continue
                    
                if not link.startswith("http"):
                    link = "https://www.towerwatch.tw" + link
                    
                if link in seen_links:
                    continue
                seen_links.add(link)
                
                title_elem = element.select_one(".title, .product-title, .name")
                title = title_elem.text.strip() if title_elem else "No Title"
                
                price_elem = element.select_one(".price, .sale-price, .product-price")
                price = price_elem.text.strip() if price_elem else "No Price"
                
                brand = None
                
                items.append({
                    "id": link,
                    "title": title,
                    "price": price,
                    "link": link,
                    "source": "TowerWatch",
                    "brand": brand
                })
                
            return items
            
        except Exception as e:
            print(f"Error in TowerWatchCrawler: {e}")
            return items
