import time
import json
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from core.scrapers.base_scraper import BaseScraper
from utils.constants import DRIVER_PATH
from core.mappings.field_mappings_vessel import FIELD_MAPPINGS
from utils.config import Config
from utils.options import ChromeOptionsBuilder  
from utils.field_utils import map_rows_by_site

loggers = Config.init_logging()
service_logger = loggers["chatservice"]

class VesselTrackerScraper(BaseScraper):
    def __init__(self, url, site_id="vesseltracker"):
        super().__init__(url)
        self.site_id = site_id
        self.scrape_type="scrapper"
        self.options = ChromeOptionsBuilder().get_options()

    def scrape(self):
        service = Service(DRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=self.options)

        try:
            driver.get(self.url)
            time.sleep(6)
            mapped_data = {}
            # 1. General Information
            gen_section = driver.find_elements(By.CSS_SELECTOR, "h2.first + div .key-value-table .row")
            for row in gen_section:
                try:
                    key = row.find_element(By.CLASS_NAME, "key").text.strip().replace(":", "")
                    value = row.find_element(By.CLASS_NAME, "value").text.strip()
                    mapped_data[key] = value
                except:
                    continue

            # 2. Course / Position
            course_section = driver.find_elements(
                By.XPATH,
                "//h2[contains(text(),'Course/Position')]/following-sibling::div[1]//div[@class='key-value-table']/div"
            )
            for row in course_section:
                try:
                    key = row.find_element(By.CLASS_NAME, "key").text.strip().replace(":", "")
                    value_elem = row.find_elements(By.CLASS_NAME, "value")
                    value = value_elem[0].text.strip() if value_elem else ""
                    mapped_data[key]= value
                except:
                    continue

            self.scrapped_data.append(mapped_data)
            mapped_data = map_rows_by_site(self.site_id,self.scrapped_data, mapping_type=self.mapping_type)
            service_logger.info(f"[SCRAPE COMPLETE] Mapped fields: {len(mapped_data[0])}")
            return mapped_data,self.scrape_type

        finally:
            driver.quit()
            service_logger.info("[SCRAPE COMPLETE] VesselTrackerScraper finished.")