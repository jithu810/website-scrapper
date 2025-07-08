import requests
import math
import time
from urllib.parse import urlparse
from typing import List, Dict
from utils.config import Config
from core.field_mappings import FIELD_MAPPINGS

loggers = Config.init_logging()
service_logger = loggers['chatservice']
# core/dp_world.py      

class DpWorldScraper:
    def __init__(self, url: str):

        service_logger.info(f"[INIT] Initializing DpWorldScraper with URL: {url}")
        self.url = url
        parsed = urlparse(url)
        self.origin = f"{parsed.scheme}://{parsed.netloc}"
        self.api_url = f"{self.origin}/api/schedule"

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
            "Referer": self.url,
            "Origin": self.origin,
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest"
        }

        self.page_size = 20
        service_logger.info(f"[INIT] DpWorldScraper initialized with API URL: {self.api_url}")

    def scrape(self,site_id) -> List[Dict]:
        all_rows = []

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
            all_rows.extend(data["table"]["rows"])

            for page in range(1, total_pages):
                payload = initial_payload.copy()
                payload["pageNumber"] = page

                service_logger.debug(f"[SCRAPE] Fetching page {page + 1}/{total_pages}")
                response = requests.post(self.api_url, headers=self.headers, data=payload, verify=False)
                response.raise_for_status()
                page_data = response.json()

                rows = page_data.get("table", {}).get("rows", [])
                service_logger.debug(f"[SCRAPE] Page {page + 1} returned {len(rows)} rows")
                all_rows.extend(rows)

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

        mapping = FIELD_MAPPINGS.get(site_id, {})
        mapped_rows = [
            {standard_key: row.get(original_key) for original_key, standard_key in mapping.items()}
            for row in all_rows
        ]

        service_logger.info(f"[SCRAPE COMPLETE] Total vessels scraped: {len(mapped_rows)}")
        return mapped_rows