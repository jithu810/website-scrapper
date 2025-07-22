# core/vessels/myshiptracking_scraper.py

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import pandas as pd
import time

from utils.constants import DRIVER_PATH
from core.scrapers.base_scraper import BaseScraper
from utils.options import ChromeOptionsBuilder  
from utils.field_utils import map_rows_by_site
from utils.config import Config

loggers = Config.init_logging()
service_logger = loggers['chatservice']

class MyShipTrackingScraper(BaseScraper):
    def __init__(self, url, site_id="myship"):
        super().__init__(url)
        self.site_id = site_id
        self.scrape_type = "scrapper"
        self.options = ChromeOptionsBuilder().get_options()
        service_logger.info(f"[INIT] MyShipTrackingScraper initialized with URL: {url} and site_id: {site_id}")

    def scrape(self):
        service_logger.info("[SCRAPE] Starting scrape process...")
        service = Service(DRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=self.options)

        combined_data = {}

        try:
            driver.get(self.url)
            service_logger.info(f"[SCRAPE] Navigated to {self.url}")
            time.sleep(5)

            # TABLE 1: table-borderless
            borderless_tables = driver.find_elements(By.CSS_SELECTOR, "table.table.table-borderless")
            service_logger.info(f"[TABLE1] Found {len(borderless_tables)} borderless tables")

            for i, table in enumerate(borderless_tables):
                html = table.get_attribute("outerHTML")
                try:
                    df = pd.read_html(html)[0]
                    if df.shape[1] == 2:
                        record = dict(zip(df.iloc[:, 0], df.iloc[:, 1]))
                        combined_data.update(record)
                    else:
                        for record in df.to_dict(orient="records"):
                            combined_data.update(record)
                    service_logger.debug(f"[TABLE1-{i}] Parsed and merged successfully")
                except Exception as e:
                    service_logger.warning(f"[TABLE1-{i}] Failed to parse HTML table: {e}")

            # TABLE 2: table-sm.my-2
            info_tables = driver.find_elements(By.CSS_SELECTOR, "table.table-sm.my-2")
            service_logger.info(f"[TABLE2] Found {len(info_tables)} info tables")

            for i, table in enumerate(info_tables):
                rows = table.find_elements(By.TAG_NAME, "tr")
                for row in rows:
                    try:
                        key_el = row.find_element(By.TAG_NAME, "th")
                        value_el = row.find_element(By.TAG_NAME, "td")
                        key = key_el.text.strip()
                        value = value_el.text.strip()
                        if key:
                            combined_data[key] = value
                    except Exception as e:
                        service_logger.debug(f"[TABLE2-{i}] Row skipped due to parsing error: {e}")
                        continue

        except Exception as e:
            service_logger.error(f"[SCRAPE] Error during scraping: {e}")
        finally:
            driver.quit()
            service_logger.info("[SCRAPE] Browser closed.")

        service_logger.info(f"[SCRAPE] Total keys extracted: {len(combined_data)}")
        self.scrapped_data.append(combined_data)
        mapped_data = map_rows_by_site(self.site_id,self.scrapped_data, mapping_type=self.mapping_type)
        service_logger.info(f"[SCRAPE] Mapping complete. Mapped records: {len(mapped_data[0])}")
        return mapped_data, self.scrape_type
