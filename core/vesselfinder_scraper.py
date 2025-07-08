# core/scrapers/vesselfinder_scraper.py
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from core.scrapers.base_scraper import BaseScraper
from utils.constants import DRIVER_PATH
from core.field_mappings_port import FIELD_MAPPINGS
from utils.config import Config

loggers = Config.init_logging()
service_logger = loggers['chatservice']

class VesselfinderScraper(BaseScraper):
    def __init__(self, url, site_id="vesselfinder"):
        super().__init__(url)
        self.site_id = site_id

    def scrape(self):
        options = Options()
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                             "AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/114.0.0.0 Safari/537.36")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--lang=en-US,en;q=0.9")

        service = Service(DRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=options)

        try:
            driver.get(self.url)
            time.sleep(5)

            raw_data = {}
            rows = driver.find_elements(By.CSS_SELECTOR, "table.aparams tr")
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) == 2:
                    key = cols[0].text.strip()
                    value = cols[1].text.strip()
                    raw_data[key] = value

            service_logger.info(f"[RAW SCRAPE] {raw_data}")

            # Filter + map using FIELD_MAPPINGS
            mapping = FIELD_MAPPINGS.get(self.site_id, {})
            mapped_data = {
                mapping[k]: v
                for k, v in raw_data.items()
                if k in mapping
            }

            service_logger.info(f"[SCRAPE COMPLETE] Vesselfinder: {len(mapped_data)} mapped fields.")
            return mapped_data  # 👈 Flat dict only with mapped fields

        finally:
            driver.quit()
