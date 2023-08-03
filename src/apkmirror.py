import requests
from selectolax.lexbor import LexborHTMLParser
from src._config import app_reference

class APKmirror(Downloader):
    def extract_download_link(self, page: str, app_name: str) -> str:
        logger.debug(f"Extracting download link from {page}")
        parser = LexborHTMLParser(self.client.get(page).text)

        href = parser.css_first("a.accent_bg").attributes["href"]

        resp = self.client.get("https://www.apkmirror.com" + href)

        parser = LexborHTMLParser(resp.text)

        href = parser.css_first(
            "p.notes:nth-child(3) > span:nth-child(1) > a:nth-child(1)"
        ).attributes["href"]

        return "https://www.apkmirror.com" + href

    def get_download_page(self, parser: LexborHTMLParser, main_page: str) -> str:
        logger.debug(f"Getting download page from {main_page}")
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
            logger.exception(
                f"Unable to find any apk on apkmirror_specific_version on {main_page}"
            )
            raise AppNotFound("Unable to find apk on apkmirror site.")

        return "https://www.apkmirror.com" + sub_url

    def specific_version(self, app_name: str, version: str) -> None:
        logger.debug(f"Trying to download {app_name}, specific version: {version}")
        version = version.replace(".", "-")
        main_page = f"{app_reference[app_name]['apkmirror']}-{version}-release/"
        parser = LexborHTMLParser(self.client.get(main_page, allow_redirects=True).text)
        download_page = self.get_download_page(parser, main_page)
        download_link = self.extract_download_link(download_page, app_name)
        self._download(download_link, f"{app_name}.apk")
        logger.debug(f"Downloaded {app_name} apk from apkmirror_specific_version")

    def latest_version(self, app_name: str, **kwargs: Any) -> None:
        logger.debug(f"Trying to download {app_name}'s latest version from apkmirror")
        page = app_reference[app_name]['apkmirror']
        if not page:
            logger.debug("Invalid app")
            raise AppNotFound("Invalid app")
        parser = LexborHTMLParser(self.client.get(page).text)
        try:
            main_page = parser.css_first(".appRowVariantTag > .accent_color").attributes["href"]
        except AttributeError:
            main_page = parser.css_first(".downloadLink").attributes["href"]

        match = re.search(r"\d", main_page)
        if not match:
            logger.error("Cannot find app main page")
            raise AppNotFound()

        main_page = "https://www.apkmirror.com" + main_page
        parser = LexborHTMLParser(self.client.get(main_page).text)
        download_page = self.get_download_page(parser, main_page)
        download_link = self.extract_download_link(download_page, app_name)
        self._download(download_link, f"{app_name}.apk")
        logger.debug(f"Downloaded {app_name} apk from apkmirror_specific_version in rt")
