import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


class Selenium:
    def __init__(self, downloads_path=None, headless=True, **kwargs):
        """
        Initializes a Selenium Chrome driver.

        Args:
            downloads_path: Directory to save files downloaded through Selenium.
            headless: Whether the driver should operate in headless mode.

        Keyword Args:
            ignore_cert_errors: If True, ignore SSL certificate errors.
            user_agent: Sets a custom user agent.
            host: Additional host argument.
            prefs: A dictionary with additional Chrome preferences.
        """
        self.options = self._create_options(downloads_path, headless, **kwargs)
        self.driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()), options=self.options
        )

    @staticmethod
    def _create_options(downloads_path, headless, **kwargs):
        """
        Generates Chrome options for the Selenium driver.

        Args:
            downloads_path: Directory to save downloads.
            headless: Whether to run the driver in headless mode.

        Keyword Args:
            ignore_cert_errors: If True, ignores SSL errors.
            user_agent: Sets a custom user agent.
            host: Additional host argument.
            prefs: A dictionary with additional Chrome preferences.

        Returns:
            Configured Chrome options.
        """
        chrome_options = Options()

        # Set the default download path.
        downloads_path = downloads_path or os.path.join(os.getcwd(), "Downloads")

        # Create a preferences dictionary.
        chrome_options.add_experimental_option(
            "prefs", {"download.default_directory": downloads_path}
        )

        # Create a preferences dictionary.
        prefs_dict = {"download.default_directory": downloads_path}
        extra_prefs = kwargs.get("prefs", {})
        for key in [
            "download.prompt_for_download",
            "download.directory_upgrade",
            "plugins.always_open_pdf_externally",
        ]:
            if key in extra_prefs:
                prefs_dict[key] = extra_prefs[key]
        chrome_options.add_experimental_option("prefs", prefs_dict)

        # Headless mode, if specified.
        if headless:
            chrome_options.add_argument("--headless")

        # Add common arguments for stability and performance.
        chrome_options.add_argument("start-maximized")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")

        # Add additional arguments based on keyword parameters.
        if kwargs.get("ignore_cert_errors", False):
            chrome_options.add_argument("--ignore-certificate-errors")
        if user_agent := kwargs.get("user_agent"):
            chrome_options.add_argument(user_agent)
        if host := kwargs.get("host"):
            chrome_options.add_argument(host)

        return chrome_options

    def get_cookies(self, website: str) -> dict:
        """
        Extracts cookies from a given website.

        Args:
            Website: The URL of the website.

        Returns:
            A dictionary of cookie names and values.

        Raises:
            ValueError: If no cookies are found.
        """
        self.driver.get(website)
        cookies = self.driver.get_cookies()
        cookie_dict = {cookie["name"]: cookie["value"] for cookie in cookies}
        if not cookie_dict:
            raise ValueError("Unable to locate cookies for the website.")
        return cookie_dict
