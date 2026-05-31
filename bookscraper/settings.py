from dotenv import load_dotenv
import os

load_dotenv()

# PROJECT SETTINGS

BOT_NAME = "bookscraper"
SPIDER_MODULES = ["bookscraper.spiders"]
NEWSPIDER_MODULE = "bookscraper.spiders"
FEED_EXPORT_ENCODING = "utf-8"
ROBOTSTXT_OBEY = False

# PERFORMANCE SETTINGS

CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 1

# FEED / OUTPUT SETTINGS

FEEDS = {
    'D:/Dev/web_scrapping/part_2/bookscraper/bookdata.csv': {
        'format': 'csv',
        'overwrite': False
    }
}

# SCRAPEOPS CONFIGURATION

SCRAPEOPS_API_KEY = os.getenv('SCRAPEOPS_API_KEY')
SCRAPEOPS_FAKE_USER_AGENT_ENDPOINT = 'http://headers.scrapeops.io/v1/user-agents?'
SCRAPEOPS_FAKE_BROWSER_HEADER_ENDPOINT = 'http://headers.scrapeops.io/v1/browser-headers?'
SCRAPEOPS_NUM_RESULTS = 50

## Feature flags — set True/False to toggle
SCRAPEOPS_FAKE_USER_AGENT_ENABLED = False
SCRAPEOPS_FAKE_BROWSER_HEADER_ENABLED = True   # active
SCRAPEOPS_PROXY_ENABLED = True                 # active
SCRAPEOPS_MONITOR_ACTIVATED = True

SCRAPEOPS_PROXY_SETTINGS = {
    'country': 'us',
}

# OXYLABS PROXY CONFIGURATION

PROXY_USER = os.getenv('PROXY_USER')
PROXY_PASSWORD = os.getenv('PROXY_PASSWORD')
PROXY_ENDPOINT = os.getenv('PROXY_ENDPOINT')
PROXY_PORT = os.getenv('PROXY_PORT')

# DOWNLOADER MIDDLEWARES
# Priority order: lower number = runs first
#
# Available middlewares:
#   ScrapeOpsFakeBrowserHeaderAgentMiddleware  — rotates browser headers
#   ScrapeOpsFakeUserAgentMiddleware           — rotates user-agents only
#   MyProxyMiddleware                          — Oxylabs Web Unblocker
#   ScrapeOpsProxyMiddleware                   — ScrapeOps Proxy API
#
# Current active stack: Browser Headers + ScrapeOps Proxy

DOWNLOADER_MIDDLEWARES = {
    # --- Header Rotation (choose one) ---
    'bookscraper.middlewares.ScrapeOpsFakeBrowserHeaderAgentMiddleware': 300,
    # 'bookscraper.middlewares.ScrapeOpsFakeUserAgentMiddleware': 300,

    # --- Proxy (choose one) ---
    'bookscraper.middlewares.ScrapeOpsProxyMiddleware': 725,
    # 'bookscraper.middlewares.MyProxyMiddleware': 350,

    # --- Retry (ScrapeOps replaces default) ---
    'scrapeops_scrapy.middleware.retry.RetryMiddleware': 550,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
}

# EXTENSIONS

EXTENSIONS = {
    'scrapeops_scrapy.extension.ScrapeOpsMonitor': 500,
}

# ITEM PIPELINES
# Priority order: lower number = runs first

ITEM_PIPELINES = {
    'bookscraper.pipelines.BookscraperPipeline': 300,
    # 'bookscraper.pipelines.SaveToMySQLPipeline': 400,
}