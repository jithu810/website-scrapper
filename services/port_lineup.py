# processors/port_lineup_processor.py
from utils.config import Config
from utils.messages import ErrorMessages, SuccessMessages
from utils.status_codes import HttpStatusCodes
from utils.timer import Timer
from utils.response_utils import response as _response
from interceptors.request_id_interceptor import request_id_ctx
from core.dp_world import DpWorldScraper
from core.portlineup.webapp import WebappScraper  # Assuming this is the correct import for webapps

loggers = Config.init_logging()
service_logger = loggers['chatservice']

SCRAPER_MAP = {
    "dpworld": DpWorldScraper, 
    "webapps": WebappScraper  
}

class PortLineupProcessor:
    def __init__(self, params: dict, context):
        service_logger.info("[INIT] PortLineupProcessor initialized.")
        self.params = params
        self.context = context

        self.query_id = params.get("QueryId")
        self.site_id = params.get("id")
        self.url = params.get("url")

        if not self.query_id:
            service_logger.warning("[INIT] Missing QueryId parameter.")
        request_id_ctx.set(self.query_id)

    def process(self):
        service_logger.info(f"[PROCESS] QueryId={self.query_id}, SiteId={self.site_id}, URL={self.url}")
        
        if not self.site_id or not self.url:
            missing = "id" if not self.site_id else "url"
            error_message = f"[MISSING PARAMS] {ErrorMessages.MISSING_PARAMS} {missing} is required."
            return _response(HttpStatusCodes.BAD_REQUEST, ErrorMessages.MISSING_PARAMS, error_message)

        scraper_class = SCRAPER_MAP.get(self.site_id.lower())
        if not scraper_class:
            error_message = f"[SCRAPER ERROR] No scraper found for id: {self.site_id}"
            return _response(HttpStatusCodes.NOT_FOUND, ErrorMessages.NOT_FOUND, error_message)

        try:
            with Timer() as total_timer:
                scraper = scraper_class(self.url)
                data = scraper.scrape(self.site_id)

            return {
                "status_code": HttpStatusCodes.OK,
                "status_description": "OK",
                "remarks": SuccessMessages.PROCESSED_SUCCESSFULLY,
                "data": {
                    "QueryId": self.query_id,
                    "ScrapedFrom": self.site_id,
                    "Extracted": data,
                    "Time": f"{total_timer.interval:.2f}s"
                }
            }

        except Exception as e:
            error_message = f"[SCRAPE ERROR] {ErrorMessages.INTERNAL_SERVER_ERROR}: {str(e)}"
            service_logger.error(error_message)
            return _response(HttpStatusCodes.INTERNAL_SERVER_ERROR, ErrorMessages.INTERNAL_SERVER_ERROR, error_message)
        
