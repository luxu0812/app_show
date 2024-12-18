from typing import List
from datetime import datetime
import requests

from app_entry import AppEntry
from config import Config

class AppStoreAPIClient:
    """
    Responsible for fetching app data from Apple's RSS API.
    This class can be extended or replaced if we want to support other data sources.
    """
    BASE_URL = "https://rss.applemarketingtools.com/api/v2"

    def fetch_top_apps(self, country: str, chart_type: str, limit: int = Config.LIMIT, allow_explicit: str = Config.ALLOW_EXPLICIT) -> List[AppEntry]:
        """
        Fetch top apps from the Apple RSS API for a given country and chart type.
        Returns a list of AppEntry (without fetched_date, country, chart_type filled yet).
        """
        url = f"{self.BASE_URL}/{country}/apps/{chart_type}/{limit}/{allow_explicit}.json"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        results = data.get('feed', {}).get('results', [])

        today_str = datetime.utcnow().strftime(Config.DATE_FORMAT)
        entries = []
        for i, app in enumerate(results, start=1):
            name = app.get('name', '')
            artist = app.get('artistName', '')
            icon = app.get('artworkUrl100', '')
            entries.append(AppEntry(
                rank=i,
                app_name=name,
                artist=artist,
                icon_url=icon,
                country=country,
                chart_type=chart_type,
                fetched_date=today_str
            ))
        return entries