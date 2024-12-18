from typing import List, Optional

from absl import logging

from app_entry import AppEntry
from apple_marketing_tools import AppStoreAPIClient
from database_manager import DatabaseManager

class ChartService:
    """
    Coordinates the workflow: checks if data is up-to-date, fetches from API if needed,
    and stores data into the database.
    """

    def __init__(self, db_manager: DatabaseManager, api_client: AppStoreAPIClient):
        self.db_manager = db_manager
        self.api_client = api_client

    def update_chart_data(self, country: str, chart_type: str) -> bool:
        """
        Ensure we have today's data for the given country and chart_type. 
        Only fetches from the API if today's data isn't available.
        """
        if self.db_manager.has_data_for_today(country, chart_type):
            logging.info(f"{country.upper()} {chart_type} apps are up-to-date. Skipping API fetch.")
            return False

        logging.info(f"Fetching {country.upper()} {chart_type} apps from API...")
        entries = self.api_client.fetch_top_apps(country, chart_type)
        self.db_manager.store_apps(entries)
        logging.info(f"Stored {chart_type} apps for {country.upper()} in local DB.")
        return True

    def get_latest_apps(self, country: str, chart_type: Optional[str] = None) -> List[AppEntry]:
        """Return the most recent stored apps for a given country and optional chart_type."""
        return self.db_manager.fetch_apps(country, chart_type=chart_type)