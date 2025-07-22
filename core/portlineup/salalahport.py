# core/scrapers/vesselfinder_scraper.py
import time
from typing import List, Dict
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from utils.constants import DRIVER_PATH
from utils.config import Config
from utils.field_utils import map_rows_by_site
from utils.options import ChromeOptionsBuilder  

loggers = Config.init_logging()
service_logger = loggers['chatservice']

class SalalahScraper:
    def __init__(self, url: str, site_id: str = "salalahport"):
        self.url = url
        self.site_id = site_id
        self.scrapped_data=[]
        self.scrape_type="selenium"
        self.mapping_type="port"
        self.options = ChromeOptionsBuilder().get_options()

    def scrape(self) -> List[Dict]:
        driver = webdriver.Chrome(service=Service(DRIVER_PATH), options=self.options)

        try:
            service_logger.info("Opening Salalah vessel schedule page...")
            driver.get(self.url)
            time.sleep(3)

            try:
                all_tab = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[text()='All Vessels']"))
                )
                all_tab.click()
                time.sleep(3)
            except Exception as e:
                service_logger.warning("'All Vessels' tab may already be active: %s", e)

            try:
                select_elem = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "dt-length-0"))
                )
                Select(select_elem).select_by_value("100")
                time.sleep(2)
            except Exception as e:
                service_logger.warning(" Failed to set entries per page: %s", e)

            # Detect pages
            pagination_buttons = driver.find_elements(By.CSS_SELECTOR, "button.dt-paging-button")
            page_numbers = [(btn.text.strip(), btn) for btn in pagination_buttons if btn.text.strip().isdigit()]
            service_logger.info(f" Pages detected: {[num for num, _ in page_numbers]}")

            for i, (num, btn) in enumerate(page_numbers):
                service_logger.info(f" Scraping page {num}...")

                if i > 0:
                    try:
                        driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                        btn.click()
                        time.sleep(3)
                    except Exception as e:
                        service_logger.warning(f" Failed to click page {num}: {e}")
                        continue

                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "#tblVessel tbody tr"))
                    )
                    rows = driver.find_elements(By.CSS_SELECTOR, "#tblVessel tbody tr")
                    service_logger.info(f" Found {len(rows)} rows on page {num}")

                    for row in rows:
                        cols = row.find_elements(By.TAG_NAME, "td")
                        if len(cols) >= 16:
                            self.scrapped_data.append({
                                "Status": cols[0].text.strip(),
                                "Vessel": cols[1].text.strip(),
                                "Rotation#": cols[2].text.strip(),
                                "Berth": cols[3].text.strip(),
                                "Line": cols[4].text.strip(),
                                "Vessel Type": cols[5].text.strip(),
                                "Call Sign": cols[6].text.strip(),
                                "Flag": cols[7].text.strip(),
                                "LOA": cols[8].text.strip(),
                                "Purpose": cols[9].text.strip(),
                                "Last Port": cols[10].text.strip(),
                                "Next Port": cols[11].text.strip(),
                                "ATA": cols[12].text.strip(),
                                "ATD": cols[13].text.strip(),
                                "ETA": cols[14].text.strip(),
                                "ETD": cols[15].text.strip()
                            })
                except Exception as e:
                    service_logger.error(f" Failed to scrape page {num}: {e}")

            service_logger.info(f" Total vessels scraped: {len(self.scrapped_data)}")
            mapped_data = map_rows_by_site(self.site_id, self.scrapped_data,mapping_type=self.mapping_type)
            service_logger.info(f"[SCRAPE COMPLETE] Total mapped vessels: {len(mapped_data)}")
            return mapped_data,self.scrape_type
        finally:
            driver.quit()
