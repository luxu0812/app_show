from absl import app
from absl import flags
from absl import logging

from config import Config
from database_manager import DatabaseManager
from apple_marketing_tools import AppStoreAPIClient
from chart_service import ChartService
from util import update_all_charts, display_all_charts

FLAGS = flags.FLAGS
flags.DEFINE_string("db_path", Config.DB_PATH, "Path to the SQLite database.")
flags.DEFINE_integer("limit", Config.LIMIT, "Limit of apps to fetch.")

def main(argv):
    logging.info(f"Args: {argv}")
    if FLAGS.db_path:
        Config.DB_PATH = FLAGS.db_path
    if FLAGS.limit:
        Config.LIMIT = FLAGS.limit

    db_manager = DatabaseManager()
    api_client = AppStoreAPIClient()
    chart_service = ChartService(db_manager, api_client)

    update_all_charts(chart_service)
    display_all_charts(chart_service)

if __name__ == "__main__":
    app.run(main)
