import requests
from selectolax.lexbor import LexborHTMLParser


class APKmirror:
    def __init__(self):
        self.client = requests.Session()
        self.client.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0"
            }
        )

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

        resp = self.client.get(
            "https://www.apkmirror.com"
            + parser.css_first("a.accent_bg").attributes["href"]
        )
        parser = LexborHTMLParser(resp.text)

        href = parser.css_first(
            "p.notes:nth-child(3) > span:nth-child(1) > a:nth-child(1)"
        ).attributes["href"]

        return "https://www.apkmirror.com" + href
