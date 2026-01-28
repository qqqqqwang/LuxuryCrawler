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

# Persistence
DATA_FILE = "seen_items.json"
