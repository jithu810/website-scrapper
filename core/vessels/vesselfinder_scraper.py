# core/scrapers/vesselfinder_scraper.py

import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from core.scrapers.base_scraper import BaseScraper
from utils.constants import DRIVER_PATH
from utils.config import Config
from utils.options import ChromeOptionsBuilder  
from utils.field_utils import map_rows_by_site

loggers = Config.init_logging()
service_logger = loggers['chatservice']

class VesselfinderScraper(BaseScraper):
    def __init__(self, url, site_id="vesselfinder"):
        super().__init__(url)
        self.site_id = site_id
        self.scrape_type = "scrapper"
        self.options = ChromeOptionsBuilder().get_options()
        service_logger.info(f"[INIT] VesselfinderScraper initialized with URL: {url}")

    def scrape(self):
        service_logger.info(f"[SCRAPE] Starting scrape for {self.site_id}")
        service = Service(DRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=self.options)

        try:
            driver.get(self.url)
            service_logger.info(f"[NAVIGATED] Opened URL: {self.url}")
            time.sleep(5)
            raw_data = {}
            rows = driver.find_elements(By.CSS_SELECTOR, "table.aparams tr")
            service_logger.info(f"[TABLE] Found {len(rows)} rows in .aparams table")

            for row in rows:
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) == 2:
                    key = cols[0].text.strip()
                    value = cols[1].text.strip()
                    if key:
                        raw_data[key] = value

            service_logger.info(f"[RAW DATA] Extracted: {raw_data}")

            self.scrapped_data.append(raw_data)
            mapped_data = map_rows_by_site(self.site_id,self.scrapped_data,mapping_type=self.mapping_type)
            service_logger.info(f"[SCRAPE COMPLETE] Mapped fields: {len(mapped_data[0])}")
            return mapped_data, self.scrape_type

        except Exception as e:
            service_logger.error(f"[SCRAPE ERROR] Exception occurred: {e}")
            return [], self.scrape_type

        finally:
            driver.quit()
            service_logger.info("[SCRAPE] Browser closed.")
