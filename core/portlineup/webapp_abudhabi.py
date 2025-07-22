import requests
import json
from urllib.parse import urlparse
from typing import List, Dict
from utils.config import Config
from utils.field_utils import map_rows_by_site
from core.scrapers.port_base_scrapper import BaseAPIScraper

loggers = Config.init_logging()
service_logger = loggers['chatservice']

class WebappScraper(BaseAPIScraper):
    def __init__(self, url: str, site_id: str = "webapps_abudhabi"):
        cookies = {
            "ASP.NET_SessionId": "u4mohrvv3mphartcbjm3g0zi",
            "TS010fd2e2": "0195c9...b35b3f"
        }

        super().__init__(url, site_id, cookies=cookies)
        self.api_url = f"{self.origin}/Public/Vessel.aspx/GetVessels"

        # Webapp-specific headers
        self.headers.update({
            "Content-Type": "application/json; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
        })

    def scrape(self) -> List[Dict]:
        status="Estimated"
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
            self.scrapped_data = json.loads(data["d"])  # Double-parsed JSON
            service_logger.info(f"[SCRAPE] Retrieved {len(self.scrapped_data)} records for status: {status}")

        except requests.RequestException as req_err:
            service_logger.error(f"[SCRAPE ERROR] Request failed: {req_err}")
            raise

        except ValueError as json_err:
            service_logger.error(f"[SCRAPE ERROR] JSON parse error: {json_err}")
            raise

        except Exception as e:
            service_logger.error(f"[SCRAPE ERROR] Unexpected error: {str(e)}")
            raise

        mapped_data= map_rows_by_site(self.site_id, self.scrapped_data,mapping_type=self.mapping_type)
        service_logger.info(f"[SCRAPE COMPLETE] Total vessels mapped: {len(mapped_data)}")
        return mapped_data,self.scrape_type
