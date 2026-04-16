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
URL_AREA02 = "https://www.area02.com/search?p=43%2C56%2C46%2C47%2C62%2C42%2C52%2C54%2C44%2C232%2C48&b=103%2C130%2C106%2C107%2C136%2C102%2C126%2C128%2C104%2C819%2C108&gp=boutique"
URL_OKURA = "https://taiwan.wb-ookura.com/collections/product-list?sort_by=created-descending"
URL_ECORING = "https://shop.eco-ring.com.tw/catalogue?tab=bargain-sale&sort=newest"

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
    "DIOR": 'https://store.2ndstreet.com.tw/v2/Search?q=%22DIOR%22&shopId=41320&order=Newest',
    "GOYARD": 'https://store.2ndstreet.com.tw/v2/Search?q=%22GOYARD%22&shopId=41320&order=Newest'
}

# Hermes URLs
HERMES_URLS = {
    "包款 (Bags)": "https://www.hermes.com/tw/zh/category/leather-goods/bags-and-clutches/#|",
    "皮件 (Small Leather Goods)": "https://www.hermes.com/tw/zh/category/leather-goods/small-leather-goods/#|"
}

# Persistence
DATA_FILE = "seen_items.json"
