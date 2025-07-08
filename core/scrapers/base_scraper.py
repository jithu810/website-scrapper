class BaseScraper:
    def __init__(self, url):
        self.url = url

    def scrape(self):
        raise NotImplementedError("Subclasses should implement this!")
