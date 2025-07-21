import requests
import json
from urllib.parse import urlparse
from typing import List, Dict
from utils.config import Config
from utils.field_utils import map_rows_by_site

loggers = Config.init_logging()
service_logger = loggers['chatservice']

class WebappScraper:
    def __init__(self, url: str,site_id: str = "webapps_abudhabi"):
        service_logger.info(f"[INIT] Initializing WebappScraper with URL: {url}")
        self.url = url
        self.site_id=site_id
        self.scrapped_data=[]
        self.scrape_type="api"

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

        mapped_data= map_rows_by_site(self.site_id, self.scrapped_data)
        service_logger.info(f"[SCRAPE COMPLETE] Total vessels mapped: {len(mapped_data)}")
        return mapped_data,self.scrape_type
