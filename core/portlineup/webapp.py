import requests
import json
import time
from urllib.parse import urlparse
from typing import List, Dict
from utils.config import Config
from core.field_mappings import FIELD_MAPPINGS

loggers = Config.init_logging()
service_logger = loggers['chatservice']

class WebappScraper:
    def __init__(self, url: str):
        service_logger.info(f"[INIT] Initializing WebappScraper with URL: {url}")
        self.url = url
        parsed = urlparse(url)
        self.origin = f"{parsed.scheme}://{parsed.netloc}"
        self.api_url = f"{self.origin}/Public/Vessel.aspx/GetVessels"

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "Content-Type": "application/json; charset=UTF-8",
            "Origin": self.origin,
            "Referer": self.url,
            "X-Requested-With": "XMLHttpRequest"
        }

        self.cookies = {
            "ASP.NET_SessionId": "u4mohrvv3mphartcbjm3g0zi",
            "TS010fd2e2": "0195c954edc4c73049822abb5293e0ebae2c28658f627ecc1c783e5acd0955747c829d152b8f6ebfa70cc0d980cd4580c174fb08cae673720f14381c15602c72f900b35b3f"
        }

    def scrape(self, site_id: str, status: str = "Estimated") -> List[Dict]:
        service_logger.info(f"[SCRAPE] Requesting vessel data with status: {status}")

        payload = {"status": status}

        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                cookies=self.cookies,
                json=payload,
                verify=False
            )
            response.raise_for_status()
            data = response.json()

            vessels = json.loads(data["d"])  # Double-parsed JSON
            service_logger.info(f"[SCRAPE] Retrieved {len(vessels)} records for status: {status}")

        except requests.RequestException as req_err:
            service_logger.error(f"[SCRAPE ERROR] Request failed: {req_err}")
            raise

        except ValueError as json_err:
            service_logger.error(f"[SCRAPE ERROR] JSON parse error: {json_err}")
            raise

        except Exception as e:
            service_logger.error(f"[SCRAPE ERROR] Unexpected error: {str(e)}")
            raise

        mapping = FIELD_MAPPINGS.get(site_id, {})
        mapped_rows = [
            {standard_key: vessel.get(original_key) for original_key, standard_key in mapping.items()}
            for vessel in vessels
        ]

        service_logger.info(f"[SCRAPE COMPLETE] Total vessels mapped: {len(mapped_rows)}")
        return mapped_rows
