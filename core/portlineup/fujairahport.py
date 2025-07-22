# core/scrapers/vesselfinder_scraper.py

import time
from typing import List, Dict
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from utils.constants import DRIVER_PATH
from utils.config import Config
from utils.field_utils import map_rows_by_site
from utils.options import ChromeOptionsBuilder  

loggers = Config.init_logging()
service_logger = loggers['chatservice']

class FujairahPort:
    def __init__(self, url: str, site_id: str = "fujairahport"):
        self.url = url
        self.site_id = site_id
        self.scrapped_data=[]
        self.scrape_type="selenium"
        self.mapping_type="port"
        self.options = ChromeOptionsBuilder().get_options()

    def scrape(self) -> List[Dict]:
        driver = webdriver.Chrome(service=Service(DRIVER_PATH), options=self.options)

        try:
            service_logger.info(f" Opening {self.site_id} vessel schedule page...")
            driver.get(self.url)
            time.sleep(5)

            soup = BeautifulSoup(driver.page_source, "html.parser")

            # Locate the vessel table
            tables = soup.find_all("table", {"border": "1"})
            vessel_table = next((t for t in tables if "Vessel_name" in t.text), None)

            if not vessel_table:
                service_logger.error(" Vessel table not found.")
                return []

            # Extract headers
            header_row = vessel_table.find("tr")
            headers = [td.get_text(strip=True).replace("\xa0", " ") for td in header_row.find_all("td")]

            # Extract data rows
            for row in vessel_table.find_all("tr")[1:]:
                cols = row.find_all("td")
                if len(cols) != len(headers):
                    continue
                self.scrapped_data.append({
                    headers[i]: cols[i].get_text(strip=True) for i in range(len(headers))
                })

            mapped_data = map_rows_by_site(self.site_id, self.scrapped_data,mapping_type=self.mapping_type)
            service_logger.info(f"[SCRAPE COMPLETE] Total mapped vessels: {len(mapped_data[0])}")
            return mapped_data,self.scrape_type
        finally:
            driver.quit()
