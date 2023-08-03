import requests
from selectolax.lexbor import LexborHTMLParser
from src._config import app_reference

class APKmirror:
    def __init__(self):
        self.client = requests.Session()
        self.client.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0)"
                + "  Gecko/20100101 Firefox/113.0"
            }
        )

    def apkmirror_get_latest_version_download_page(self, app_name: str) -> dict:
        page = f"https://www.apkmirror.com/apk/{app_name}/"

        res = self.client.get(page)

        parser = LexborHTMLParser(res.text)

        version = parser.css_first("span.file").text().strip().split(" ")[0]
        download_link = parser.css_first(".listWidgetDownloadLink").attributes["href"]

        return {
            "version": version,
            "url": "https://www.apkmirror.com" + download_link,
        }

    def get_specific_version_download_page(self, app_name: str, version: str) -> str:
        page = f"https://www.apkmirror.com/apk/{app_name}/{version}/"

        try:
            res = self.client.get(page)
        except Exception as e:
            raise Exception("Error retrieving download page") from e

        parser = LexborHTMLParser(res.text)

        download_link = parser.css_first(".listWidgetDownloadLink").attributes["href"]

        return "https://www.apkmirror.com" + download_link

    def extract_download_link(self, page: str) -> str:
        res = self.client.get(page)

        parser = LexborHTMLParser(res.text)

        download_link = parser.css_first(".downloadButton").attributes["href"]

        return "https://www.apkmirror.com" + download_link
