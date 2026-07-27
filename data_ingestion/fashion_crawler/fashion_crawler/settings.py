# Scrapy settings for fashion_crawler project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "fashion_crawler"

SPIDER_MODULES = ["fashion_crawler.spiders"]
NEWSPIDER_MODULE = "fashion_crawler.spiders"

ADDONS = {}

COOKIES_ENABLED = True

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = "fashion_crawler (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Concurrency and throttling settings
#CONCURRENT_REQUESTS = 2
#CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 3.0

RANDOMIZE_DOWNLOAD_DELAY = 0.5

DEPTH_PRIORITY = 1
SCHEDULER_DISK_QUEUE = 'scrapy.squeues.PickleFifoDiskQueue'
SCHEDULER_MEMORY_QUEUE = 'scrapy.squeues.FifoMemoryQueue'

FEEDS = {
    "s3://sogo-fashion-bucket/moda-operandi/data_%(time)s.json": {
    "format": "json",
    "encoding": "utf8",
    "store_empty": False
    }
}

ITEM_PIPELINE = {
    'fashion_scraper.pipelines.FashionScraperPipeline':300
}


TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

AUTOTHROTTLE_ENABLED = True

AUTOTHROTTLE_START_DELAY = 3.0

AUTOTHROTTLE_MAX_DELAY = 15

DOWNLOAD_TIMEOUT = 40

#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

LOG_LEVEL = "INFO"
# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:

# Source - https://stackoverflow.com/a/55582803
# Posted by Andres Mitre
# Retrieved 2026-07-23, License - CC BY-SA 4.0

HTTPERROR_ALLOWED_CODES  =[404, 403]


headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9,el;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}


# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "fashion_crawler.middlewares.FashionCrawlerSpiderMiddleware": 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    "fashion_crawler.middlewares.FashionCrawlerDownloaderMiddleware": 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    "fashion_crawler.pipelines.FashionCrawlerPipeline": 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
#FEED_EXPORT_ENCODING = "utf-8"
