from selenium.webdriver.chrome.options import Options

class ChromeOptionsBuilder:
    def __init__(self):
        self.options = Options()
        self._set_default_options()

    def _set_default_options(self):
        self.options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--window-size=1920,1080")
        self.options.add_argument("--lang=en-US,en;q=0.9")

    def get_options(self):
        return self.options
