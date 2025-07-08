import time
import json
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from core.scrapers.base_scraper import BaseScraper
from utils.constants import DRIVER_PATH
from core.field_mappings_port import FIELD_MAPPINGS
from utils.config import Config

loggers = Config.init_logging()
service_logger = loggers["chatservice"]


class VesselTrackerScraper(BaseScraper):
    def __init__(self, url, site_id="vesseltracker"):
        super().__init__(url)
        self.site_id = site_id

    def scrape(self):
        options = Options()
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                             "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--lang=en-US,en;q=0.9")

        service = Service(DRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=options)

        try:
            driver.get(self.url)
            time.sleep(6)

            mapping = FIELD_MAPPINGS.get(self.site_id, {})
            mapped_data = {}

            # 1. General Information
            gen_section = driver.find_elements(By.CSS_SELECTOR, "h2.first + div .key-value-table .row")
            for row in gen_section:
                try:
                    key = row.find_element(By.CLASS_NAME, "key").text.strip().replace(":", "")
                    value = row.find_element(By.CLASS_NAME, "value").text.strip()
                    if key in mapping:
                        mapped_data[mapping[key]] = value
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
                    if key in mapping:
                        mapped_data[mapping[key]] = value
                except:
                    continue

            # 3. Latest Ports
            latest_ports = []
            port_rows = driver.find_elements(
                By.XPATH,
                "//h2[contains(text(),'Latest ports')]/following-sibling::div[1]/div[contains(@class,'row') and not(contains(@class,'table-header'))]"
            )
            for row in port_rows:
                try:
                    cols = row.find_elements(By.CLASS_NAME, "col-xs-3")
                    if len(cols) >= 3:
                        latest_ports.append({
                            "arrival": cols[0].text.strip(),
                            "departure": cols[1].text.strip(),
                            "duration": cols[2].text.strip()
                        })
                except:
                    continue
            if latest_ports:
                pass
                # mapped_data["latest_ports"] = latest_ports

            # 4. Latest Waypoints
            waypoints = []
            wp_rows = driver.find_elements(
                By.XPATH,
                "//h2[contains(text(),'Latest Waypoints')]/following-sibling::div[1]/div[contains(@class,'row') and not(contains(@class,'table-header'))]"
            )
            for row in wp_rows:
                try:
                    name = row.find_elements(By.CLASS_NAME, "col-xs-5")[0].text.strip()
                    time_ = row.find_elements(By.CLASS_NAME, "col-xs-4")[0].text.strip()
                    direction = row.find_elements(By.CLASS_NAME, "col-xs-2")[0].text.strip()
                    waypoints.append({"waypoint": name, "time": time_, "direction": direction})
                except:
                    continue
            if waypoints:
                pass
                # mapped_data["latest_waypoints"] = waypoints

            # 5. Daily Chart Data
            page_source = driver.page_source
            pattern = r"data: (\[.*?\])"
            match = re.search(pattern, page_source)
            if match:
                try:
                    data_str = match.group(1).replace("x", '"x"').replace("y", '"y"')
                    chart_data = json.loads(data_str)
                    # mapped_data["daily_average_speed"] = chart_data
                except:
                    pass
                    # mapped_data["daily_average_speed"] = []

            service_logger.info(f"[SCRAPE COMPLETE] Vesseltracker: {len(mapped_data)} fields extracted.")
            return mapped_data

        finally:
            driver.quit()
            service_logger.info("[SCRAPE COMPLETE] VesselTrackerScraper finished.")