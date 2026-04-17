import csv
import logging

class SweetSpotMatcher:
    def __init__(self, csv_url_or_path):
        self.targets = []
        self._load_targets(csv_url_or_path)

    def _load_targets(self, csv_url_or_path):
        try:
            if csv_url_or_path.startswith('http'):
                import requests
                import io
                response = requests.get(csv_url_or_path)
                response.raise_for_status()
                # Ensure correct encoding processing (utf-8-sig handles BOM)
                response.encoding = 'utf-8-sig'
                f = io.StringIO(response.text)
            else:
                f = open(csv_url_or_path, 'r', encoding='utf-8-sig')

            with f:
                reader = csv.DictReader(f)
                for row in reader:
                    target = {}
                    for k, v in row.items():
                        if k is None or v is None: continue
                        clean_key = k.strip()
                        target[clean_key] = v.strip()
                    
                    try:
                        price_str = target['甜漏價'].replace(',', '').strip()
                        target['甜漏價'] = int(float(price_str)) # Handle possible floats
                    except (ValueError, TypeError):
                        continue 
                    
                    self.targets.append(target)
            
            # Debug info to verify data freshness
            brand_counts = {}
            for t in self.targets:
                b = t.get('品牌', 'Unknown')
                brand_counts[b] = brand_counts.get(b, 0) + 1
            
            logging.info(f"Loaded {len(self.targets)} sweet spot targets from {csv_url_or_path}")
            logging.info(f"Top brands in targets: {dict(list(brand_counts.items())[:10])}")
            
            # Specifically log if test rules are found
            test_rules = [t for t in self.targets if t.get('甜漏價') == 500000]
            if test_rules:
                logging.info(f"DATA VERIFIED: Found {len(test_rules)} active test rules (Price=500,000)")
            else:
                logging.warning("DATA ALERT: No 500,000 price rules found in the loaded CSV!")

        except Exception as e:
            logging.error(f"Failed to load sweet spot targets: {e}")

    def _check_string_match(self, condition_str, text, is_or=True):
        if not condition_str:
            return True # Empty condition means match
        
        # Split by comma or pipe for OR
        parts = [p.strip().lower() for p in condition_str.replace('|', ',').split(',') if p.strip()]
        
        if not parts:
            return True
            
        text_lower = text.lower()
        if is_or:
            return any(p in text_lower for p in parts)
        else:
            return all(p in text_lower for p in parts)

    def check_item(self, item_brand, item_title, item_price):
        """
        Check if an item matches the sweet spot criteria.
        Returns: (is_sweet_spot (bool), is_high_confidence (bool), target_info (dict|None))
        """
        if not item_title or item_price is None or item_price <= 0:
            return False, False, None
            
        item_title_lower = item_title.lower()
        item_brand_lower = (item_brand or "").lower()
        
        for target in self.targets:
            # 1. Check Brand (either specified in item_brand or found in title)
            target_brand = target.get('品牌', '').lower()
            if target_brand not in item_brand_lower and target_brand not in item_title_lower:
                continue
                
            # 2. Check Price
            if item_price > target['甜漏價']:
                continue
                
            # 3. Check Model Keywords (OR logic)
            model_keywords_str = target.get('包款關鍵字', '')
            # Match against BOTH title and brand name
            full_text_to_check = f"{item_title_lower} {item_brand_lower}"
            if not self._check_string_match(model_keywords_str, full_text_to_check, is_or=True):
                continue
                
            # If we reach here, Core Match is SUCCESS!
            
            # 4. Calculate Confidence based on auxiliary fields
            missing_info = []
            
            # Leather Check
            leather_val = target.get('皮質', '')
            if leather_val and not self._check_string_match(leather_val, item_title_lower, is_or=True):
                missing_info.append("皮質")
                
            # Color Check
            color_val = target.get('顏色', '')
            if color_val and not self._check_string_match(color_val, item_title_lower, is_or=True):
                missing_info.append("顏色")
                
            # Stamp Check
            stamp_val = target.get('年份_刻印', '')
            if stamp_val and not self._check_string_match(stamp_val, item_title_lower, is_or=True):
                missing_info.append("年份")
                
            # Accessory Check
            acc_val = target.get('配件', '')
            if acc_val and not self._check_string_match(acc_val, item_title_lower, is_or=True):
                missing_info.append("配件")
                
            is_high_confidence = len(missing_info) == 0
            
            # Attach missing info so notifier can explain it
            target_info_result = target.copy()
            target_info_result['missing_info'] = missing_info
            
            return True, is_high_confidence, target_info_result
            
        return False, False, None
