import time

from absl import logging

from config import Config
from chart_service import ChartService

def update_all_charts(chart_service: ChartService):
    for territory in Config.TERRITORIES:
        for chart_type in Config.CHART_TYPES:
            if chart_service.update_chart_data(territory, chart_type):
                time.sleep(10)

def display_all_charts(chart_service: ChartService):
    for territory in Config.TERRITORIES:
        logging.info(f"\n=== {territory.upper()} Data ===")
        for chart in Config.CHART_TYPES:
            apps = chart_service.get_latest_apps(territory, chart)
            if not apps:
                logging.info(f"No {chart} apps found for {territory.upper()}.")
                continue
            
            top_app_icon = apps[0].icon_url
            fetched_date = apps[0].fetched_date
            logging.info(f"\nChart: {chart}")
            logging.info(f"Data Fetched On: {fetched_date}")
            logging.info(f"Top-1 App Icon: {top_app_icon}")
            logging.info(f"Rank | App Name               | Artist")
            logging.info("-"*60)
            for app in apps:
                logging.info(f"{app.rank:<4} | {app.app_name[:25]:<25} | {app.artist[:20]}")