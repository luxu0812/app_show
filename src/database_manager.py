from datetime import datetime
from typing import List, Optional
import pandas as pd
import sqlite3

from app_entry import AppEntry
from config import Config

class DatabaseManager:
    """
    Responsible for all database interactions.
    Implements a repository-like pattern for AppEntry.
    """
    def __init__(self, db_path: str = Config.DB_PATH):
        self.db_path = db_path
        self._initialize_database()

    def _initialize_database(self) -> None:
        """Create the table if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS top_apps (
                country TEXT,
                chart_type TEXT,
                rank INTEGER,
                app_name TEXT,
                artist TEXT,
                icon_url TEXT,
                fetched_date TEXT,
                PRIMARY KEY (country, chart_type, rank, fetched_date)
            )
        """)
        conn.commit()
        conn.close()

    def store_apps(self, entries: List[AppEntry]) -> None:
        """Store a list of AppEntry objects into the database."""
        if not entries:
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        for entry in entries:
            cursor.execute("""
                INSERT OR REPLACE INTO top_apps (country, chart_type, rank, app_name, artist, icon_url, fetched_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (entry.country, entry.chart_type, entry.rank, entry.app_name, entry.artist, entry.icon_url, entry.fetched_date))
        conn.commit()
        conn.close()
    
    def has_data_for_today(self, country: str, chart_type: str) -> bool:
        """Check if today's data for the given country and chart_type is already stored."""
        today_str = datetime.utcnow().strftime(Config.DATE_FORMAT)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) 
            FROM top_apps
            WHERE country = ? AND chart_type = ? AND fetched_date = ?
        """, (country, chart_type, today_str))
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0

    def fetch_apps(self, country: str, chart_type: Optional[str] = None, date_str: Optional[str] = None) -> List[AppEntry]:
        """
        Fetch apps from the database for a given country and optionally a chart_type and date.
        If date_str is None, fetches the most recent data for that country/chart_type.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Determine the date if not provided
        if date_str is None:
            if chart_type is None:
                cursor.execute("""
                    SELECT MAX(fetched_date) FROM top_apps WHERE country = ?
                """, (country,))
            else:
                cursor.execute("""
                    SELECT MAX(fetched_date) FROM top_apps WHERE country = ? AND chart_type = ?
                """, (country, chart_type))
            result = cursor.fetchone()
            date_str = result[0] if result else None
            if date_str is None:
                conn.close()
                return []

        # Fetch entries
        if chart_type is None:
            cursor.execute("""
                SELECT rank, app_name, artist, icon_url, fetched_date, country, chart_type
                FROM top_apps
                WHERE country = ? AND fetched_date = ?
                ORDER BY chart_type, rank
            """, (country, date_str))
        else:
            cursor.execute("""
                SELECT rank, app_name, artist, icon_url, fetched_date, country, chart_type
                FROM top_apps
                WHERE country = ? AND chart_type = ? AND fetched_date = ?
                ORDER BY rank
            """, (country, chart_type, date_str))

        rows = cursor.fetchall()
        conn.close()

        entries = [
            AppEntry(rank=r[0], app_name=r[1], artist=r[2], icon_url=r[3],
                     fetched_date=r[4], country=r[5], chart_type=r[6])
            for r in rows
        ]
        return entries
    
    def fetch_apps_name_from_all_countries(self, chart_type: Optional[str] = None, limit=Config.LIMIT):
        """
        Get a list of distinct apps that appear in the top `limit` of `chart_type` apps
        for the latest fetched_date in the database.
        """
        conn = sqlite3.connect(self.db_path)
        query = f"""
            WITH latest AS (
                SELECT MAX(fetched_date) AS max_date
                FROM top_apps
                WHERE chart_type = ?
            )
            SELECT DISTINCT app_name
            FROM top_apps
            JOIN latest ON top_apps.fetched_date = latest.max_date
            WHERE chart_type = ?
            AND rank <= ?
            ORDER BY app_name COLLATE NOCASE
        """
        apps = pd.read_sql_query(query, conn, params=(chart_type, chart_type, limit))
        conn.close()
        return apps['app_name'].tolist()

    def get_countries_for_app(self, app_name, chart_type: Optional[str] = None, limit=Config.LIMIT):
        """
        Given an app_name, return all countries where this app is in the top `limit` free apps.
        """
        conn = sqlite3.connect(self.db_path)
        query = f"""
            SELECT DISTINCT country
            FROM top_apps
            WHERE chart_type = ?
            AND rank <= ?
            AND app_name = ?
        """
        countries = pd.read_sql_query(query, conn, params=(chart_type, limit, app_name))
        conn.close()
        return countries['country'].tolist()
    
    def get_app_icon(self, chart_type, app_name):
        """
        Retrieve the icon_url for the given app from the database for the given chart_type.
        """
        conn = sqlite3.connect(self.db_path)
        query = """
            WITH latest AS (
                SELECT MAX(fetched_date) AS max_date
                FROM top_apps
                WHERE chart_type = ?
            )
            SELECT icon_url FROM top_apps
            JOIN latest ON top_apps.fetched_date = latest.max_date
            WHERE chart_type = ?
            AND rank <= ?
            AND app_name = ?
            LIMIT 1
        """
        row = conn.execute(query, (chart_type, chart_type, Config.LIMIT, app_name)).fetchone()
        conn.close()
        if row:
            return row[0]
        return None