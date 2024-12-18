import requests
import re
from urllib.parse import urlparse, parse_qs
from google_play_scraper import app as gp_app

class MobileAppInfoFetcher:
    def __init__(self):
        # No url on init; we handle URLs dynamically in get_app_info
        pass

    def get_app_info(self, url):
        """
        Given a URL, automatically detect if it's from Apple App Store or Google Play Store,
        then fetch and return the (app_name, app_icon_url). If unsupported or failure, return (None, None).
        """
        platform = self._detect_platform(url)
        if platform == "apple":
            return self._fetch_apple_app_info(url)
        elif platform == "google":
            return self._fetch_google_app_info(url)
        else:
            return None, None

    def _detect_platform(self, url):
        """
        Detect whether the URL is from the Apple App Store or Google Play Store.
        Returns 'apple', 'google', or None.
        """
        parsed = urlparse(url.lower())
        if "apps.apple.com" in parsed.netloc:
            return "apple"
        elif "play.google.com" in parsed.netloc:
            return "google"
        return None

    def _fetch_apple_app_info(self, url):
        """
        Fetch app name and icon from Apple App Store URL using iTunes Lookup API.
        """
        match = re.search(r'id(\d+)', url)
        if not match:
            return None, None
        app_id = match.group(1)

        api_url = f"https://itunes.apple.com/lookup?id={app_id}"
        resp = requests.get(api_url)
        if resp.status_code != 200:
            return None, None

        data = resp.json()
        if data.get('results'):
            result = data['results'][0]
            app_name = result.get('trackName')
            app_icon = result.get('artworkUrl100')
            return app_name, app_icon
        return None, None

    def _fetch_google_app_info(self, url):
        """
        Fetch app name and icon from Google Play Store URL using google-play-scraper.
        """
        pkg_name = self._extract_package_name_from_google_url(url)
        if not pkg_name:
            return None, None

        try:
            result = gp_app(pkg_name, lang='en', country='us')
            app_name = result.get('title')
            app_icon = result.get('icon')
            return app_name, app_icon
        except:
            return None, None

    @staticmethod
    def _extract_package_name_from_google_url(url):
        """
        Extract the package name (id param) from a Google Play URL.
        """
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        package_name = query.get("id", [None])[0]
        return package_name


# Example Usage:
if __name__ == "__main__":
    fetcher = MobileAppInfoFetcher()

    # Apple App Store URL example
    apple_url = "https://apps.apple.com/us/app/tile-family-match-puzzle-game/id6444056676"
    name_apple, icon_apple = fetcher.get_app_info(apple_url)
    print("Apple App Name:", name_apple)
    print("Apple App Icon:", icon_apple)

    # Google Play Store URL example
    google_url = "https://play.google.com/store/apps/details?id=com.peoplefun.wordcross"
    name_google, icon_google = fetcher.get_app_info(google_url)
    print("Google App Name:", name_google)
    print("Google App Icon:", icon_google)
