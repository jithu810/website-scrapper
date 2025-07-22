class BaseScraper:
    def __init__(self, url):
        self.url = url
        self.scrapped_data = []
        self.mapping_type="vessel"

    def scrape(self):
        raise NotImplementedError("Subclasses should implement this!")
