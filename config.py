import os

# Telegram Config
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# Support multiple chat IDs separated by comma
TELEGRAM_CHAT_IDS = os.getenv("TELEGRAM_CHAT_ID", "").split(",")

# Crawler Config
# This is now controlled by GitHub Actions schedule, but we keep a fallback or unused const
CHECK_INTERVAL_MINUTES = 15 

# URLs
URL_2NDSTREET = "https://store.2ndstreet.com.tw/v2/official/SalePageCategory/442462?sortMode=Newest"
URL_POPCHILL = "https://www.popchill.com/zh-TW/new_products"

# Filter Config
EXCLUDED_KEYWORDS = ["Coach", "Tory Burch"]

# 2nd Street Brand Search URLs
SECOND_STREET_BRANDS = {
    "LV": "https://store.2ndstreet.com.tw/v2/Search?q=LOUIS+VUITTON&shopId=41320&order=Newest",
    "CHANEL": "https://store.2ndstreet.com.tw/v2/Search?q=CHANEL&shopId=41320&order=Newest",
    "HERMES": "https://store.2ndstreet.com.tw/v2/Search?q=HERMES&shopId=41320&startIndex=0&order=Newest",
    "CELINE": "https://store.2ndstreet.com.tw/v2/Search?q=CELINE&shopId=41320&order=Newest",
    "BURBERRY": "https://store.2ndstreet.com.tw/v2/Search?q=BURBERRY&shopId=41320&order=Newest",
    "BALENCIAGA": "https://store.2ndstreet.com.tw/v2/Search?q=BALENCIAGA&shopId=41320&order=Newest",
    "GUCCI": "https://store.2ndstreet.com.tw/v2/Search?q=GUCCI&shopId=41320&order=Newest",
    "MIU MIU": 'https://store.2ndstreet.com.tw/v2/Search?q=%22MIU+MIU%22&shopId=41320&order=Newest',
    "PRADA": 'https://store.2ndstreet.com.tw/v2/Search?q=%22PRADA%22&shopId=41320&order=Newest',
    "DIOR": 'https://store.2ndstreet.com.tw/v2/Search?q=%22DIOR%22&shopId=41320&order=Newest'
}

# Persistence
DATA_FILE = "seen_items.json"
