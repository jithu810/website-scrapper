# core/scrapers/base_scraper.py
import requests
from urllib.parse import urlparse
from utils.config import Config

loggers = Config.init_logging()
service_logger = loggers['chatservice']

class BaseAPIScraper:
    def __init__(self, url: str, site_id: str, default_headers: dict = None, cookies: dict = None):
        self.url = url
        self.site_id = site_id
        self.scrapped_data = []
        self.scrape_type = "api"
        self.mapping_type="port"

        parsed = urlparse(url)
        self.origin = f"{parsed.scheme}://{parsed.netloc}"
        self.api_url = ""  # To be set by child class

        # Default headers
        self.headers = default_headers or {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Referer": url,
            "Origin": self.origin,
        }

        self.cookies = cookies or {}

        service_logger.info(f"[INIT] {self.__class__.__name__} initialized for site_id: {site_id}")
