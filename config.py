import os

# Telegram Config
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# Support multiple chat IDs separated by comma
TELEGRAM_CHAT_IDS = os.getenv("TELEGRAM_CHAT_ID", "").split(",")
SWEET_SPOT_TG_CHAT_ID = os.getenv("SWEET_SPOT_TG_CHAT_ID", "-5234775671")

# Sweet Spot Target List
TARGET_LIST_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTI1lVm7yebr_c2YFVYaCrcorVfj9vg5pXjcK4Bxw6PsSWJCXXaLdE4Me9m__6PDCEOo3OGScSMSKp6/pub?output=csv"

# Crawler Config
# This is now controlled by GitHub Actions schedule, but we keep a fallback or unused const
CHECK_INTERVAL_MINUTES = 15 

# URLs
URL_2NDSTREET = "https://store.2ndstreet.com.tw/v2/official/SalePageCategory/442462?sortMode=Newest"
URL_POPCHILL = "https://www.popchill.com/zh-TW/new_products"
URL_AREA02 = "https://www.area02.com/zh-TW/tag/boutique"
URL_OKURA = "https://taiwan.wb-ookura.com/collections/product-list?sort_by=created-descending"
URL_ECORING = "https://shop.eco-ring.com.tw/catalogue?tab=bargain-sale&sort=newest"
URL_FUGETSU = "https://brandfugetsu.com/Form/Product/ProductList.aspx?cicon=1&udns=1"

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
    "GOYARD": 'https://store.2ndstreet.com.tw/v2/Search?q=%22GOYARD%22&shopId=41320&order=Newest',
    "ISSEY MIYAKE": "https://store.2ndstreet.com.tw/v2/Search?q=ISSEY+MIYAKE&shopId=41320&order=Newest"
}

# Hermes URLs
HERMES_URLS = {
    "包款 (Bags)": "https://www.hermes.com/tw/zh/category/leather-goods/bags-and-clutches/#|",
    "皮件 (Small Leather Goods)": "https://www.hermes.com/tw/zh/category/leather-goods/small-leather-goods/#|"
}

# Persistence
DATA_FILE = "seen_items.json"
