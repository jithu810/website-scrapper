from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import time

from utils.constants import DRIVER_PATH
from core.scrapers.base_scraper import BaseScraper
from core.field_mappings_port import FIELD_MAPPINGS

class MyShipTrackingScraper(BaseScraper):
    def __init__(self, url, site_id="myship"):
        super().__init__(url)
        self.site_id = site_id

    def scrape(self):
        options = Options()
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                             "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")

        service = Service(DRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(self.url)
        time.sleep(5)

        all_tables_json = []

        # 🔹 TABLE 1: <table class="table table-borderless">
        borderless_tables = driver.find_elements(By.CSS_SELECTOR, "table.table.table-borderless")
        for table in borderless_tables:
            html = table.get_attribute("outerHTML")
            df = pd.read_html(html)[0]

            if df.shape[1] == 2:
                record = dict(zip(df.iloc[:, 0], df.iloc[:, 1]))
                all_tables_json.append(record)
            else:
                all_tables_json.extend(df.to_dict(orient="records"))

        # 🔹 TABLE 2: <table class="table-sm my-2">
        info_tables = driver.find_elements(By.CSS_SELECTOR, "table.table-sm.my-2")
        for table in info_tables:
            rows = table.find_elements(By.TAG_NAME, "tr")
            record = {}
            for row in rows:
                try:
                    key_el = row.find_element(By.TAG_NAME, "th")
                    value_el = row.find_element(By.TAG_NAME, "td")
                    key = key_el.text.strip()
                    value = value_el.text.strip()
                    if key.lower() == "flag":
                        value = value_el.text.strip()
                    if key:
                        record[key] = value
                except Exception:
                    continue
            if record:
                all_tables_json.append(record)

        driver.quit()

        # 🔄 Merge & Filter: apply mapping and return only mapped fields
        mapping = FIELD_MAPPINGS.get(self.site_id, {})
        merged_data = {}
        for item in all_tables_json:
            for k, v in item.items():
                k_clean = k.strip()
                mapped_key = mapping.get(k_clean)
                if mapped_key:
                    merged_data[mapped_key] = v

        return merged_data  # 👈 Single flat dictionary
