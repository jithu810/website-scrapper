import requests
import math
import time
from urllib.parse import urlparse
from typing import List, Dict
from utils.config import Config
from utils.field_utils import map_rows_by_site
from core.scrapers.port_base_scrapper import BaseAPIScraper

loggers = Config.init_logging()
service_logger = loggers['chatservice']

class DpWorldScraper(BaseAPIScraper):
    def __init__(self, url: str, site_id: str = "dpworld"):
        super().__init__(url, site_id)
        self.page_size = 20
        self.api_url = f"{self.origin}/api/schedule"

        # You can override headers if needed
        self.headers.update({
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
        })

    def scrape(self) -> List[Dict]:

        initial_payload = {
            "ApiName": "VesselSchedule|Caucedo",
            "Type": "",
            "Columns[]": [
                "VesselName", "ATA", "ATD", "ETA", "ETD", "Line_Operator", "Phase", "VoyageNo"
            ],
            "pageNumber": 0,
            "pageSize": self.page_size
        }

        try:
            service_logger.info(f"[SCRAPE] Sending initial request to {self.api_url}")
            response = requests.post(self.api_url, headers=self.headers, data=initial_payload, verify=False)
            response.raise_for_status()
            data = response.json()

            total_count = data["table"]["Totalcount"]
            total_pages = math.ceil(total_count / self.page_size)

            service_logger.info(f"[SCRAPE] Total records: {total_count}, Total pages: {total_pages}")
            self.scrapped_data.extend(data["table"]["rows"])

            for page in range(1, total_pages):
                payload = initial_payload.copy()
                payload["pageNumber"] = page

                service_logger.debug(f"[SCRAPE] Fetching page {page + 1}/{total_pages}")
                response = requests.post(self.api_url, headers=self.headers, data=payload, verify=False)
                response.raise_for_status()
                page_data = response.json()

                rows = page_data.get("table", {}).get("rows", [])
                service_logger.debug(f"[SCRAPE] Page {page + 1} returned {len(rows)} rows")
                self.scrapped_data.extend(rows)

                time.sleep(0.5)  # Polite delay

        except requests.RequestException as req_err:
            service_logger.error(f"[SCRAPE ERROR] Request failed: {req_err}")
            raise

        except ValueError as json_err:
            service_logger.error(f"[SCRAPE ERROR] Invalid JSON received: {json_err}")
            raise

        except Exception as e:
            service_logger.error(f"[SCRAPE ERROR] Unexpected error: {str(e)}")
            raise

        mapped_data = map_rows_by_site(self.site_id,self.scrapped_data,mapping_type=self.mapping_type)
        service_logger.info(f"[SCRAPE COMPLETE] Total vessels scraped: {len(mapped_data)}")
        return mapped_data,self.scrape_type