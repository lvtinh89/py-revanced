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
        page = f"{app_reference[app_name]['apkmirror']}"

        res = self.client.get(page)

        parser = LexborHTMLParser(res.text)

        version = parser.css_first(
            "div.p-relative:nth-child(4) > div:nth-child(2) > div:nth-child(1) >"
            + " div:nth-child(1) > div:nth-child(2) >"
            + " div:nth-child(1) > h5:nth-child(1) > a:nth-child(1)"
        ).text()

        download_link = parser.css_first(".downloadLink").attributes["href"]

        return {
            "version": version.split(" ")[1],
            "url": "https://www.apkmirror.com" + download_link,
        }

    def get_download_page(self, url: str) -> str:
        parser = LexborHTMLParser(self.client.get(url, timeout=10).text)

        apm = parser.css(".apkm-badge")

        sub_url = ""
        for is_apm in apm:
            parent_text = is_apm.parent.parent.text()

            if "APK" in is_apm.text() and (
                "arm64-v8a" in parent_text
                or "universal" in parent_text
                or "noarch" in parent_text
            ):
                parser = is_apm.parent
                sub_url = parser.css_first(".accent_color").attributes["href"]
                break
        if sub_url == "":
            raise Exception("No download page found")

        return "https://www.apkmirror.com" + sub_url

    def extract_download_link(self, page: str) -> None:
        parser = LexborHTMLParser(self.client.get(page).text)

        # Span class apkm-badge with text APK
        apk_span = parser.css_first(
            "div.table-row:nth-child(3) > div:nth-child(1) > span:nth-child(2)"
        )

        if not apk_span:
            raise Exception("No download link found")

        download_url = apk_span.parent.css_first("a").attributes["href"]

        resp = self.client.get("https://www.apkmirror.com" + download_url)

        parser = LexborHTMLParser(resp.text)

        href = parser.css_first("a.accent_bg").attributes["href"]

        resp = self.client.get("https://www.apkmirror.com" + href)

        parser = LexborHTMLParser(resp.text)

        href = parser.css_first(
            "p.notes:nth-child(3) > span:nth-child(1) > a:nth-child(1)"
        ).attributes["href"]

        return "https://www.apkmirror.com" + href
