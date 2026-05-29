import requests
import json
import urllib.parse
from .base import Crawler

class Area02Crawler(Crawler):
    def get_new_items(self):
        items = []
        try:
            url = "https://api.area02.com/api/node/search"
            # Extract luxury series/brands from Area02's API
            facet_filters = [
                [
                    "series_id:102", "series_id:103", "series_id:104", 
                    "series_id:106", "series_id:107", "series_id:108", 
                    "series_id:126", "series_id:128", "series_id:130", 
                    "series_id:136", "series_id:819"
                ]
            ]
            
            payload = {
                "requests": [{
                    "indexName": "prod_node",
                    "params": {
                        "clickAnalytics": True,
                        "facetFilters": facet_filters,
                        "page": 0,
                        "hitsPerPage": 100,
                        "query": ""
                    }
                }]
            }
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            
            resp = requests.post(url, json=payload, headers=headers, timeout=15)
            if resp.status_code != 200:
                print(f"[Area02] Failed to fetch API, status: {resp.status_code}")
                return items
                
            data = resp.json()
            hits = data.get('results', [{}])[0].get('hits', [])
            
            print(f"[Area02] Found {len(hits)} luxury items via API.")
            
            for h in hits:
                title = h.get('name_en') or h.get('name') or h.get('title')
                if not title:
                    continue
                    
                price_val = h.get('price_info', {}).get('TWD', 0)
                price = f"NT$ {int(price_val):,}" if price_val else "NT$ 0"
                
                hash_key = h.get('hash_key')
                brand = h.get('brand')
                
                if not hash_key or not brand:
                    continue
                    
                brand_path = brand.lower().replace(' ', '-')
                slug = urllib.parse.quote(title.replace(' ', '-').replace('/', '-').lower())
                
                link = f"https://www.area02.com/{brand_path}/{brand_path}/i-{hash_key}--{slug}"
                
                items.append({
                    "id": link,
                    "title": title,
                    "price": price,
                    "link": link,
                    "source": "Area02"
                })
                
        except Exception as e:
            print(f"Error in Area02Crawler: {e}")
            
        return items

