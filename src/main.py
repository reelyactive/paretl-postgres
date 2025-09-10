import json
import logging
import time
import psutil
import psycopg2
import pandas as pd
import argparse

from datetime import datetime

from src.logger_setup import setup_logging
from src.config_loader import load_config
from src.db_connector import DBConnector

from src.data.data_wrangler import DataWrangler
from src.data.data_filter import DataFilter
from src.data.data_extractor import DataExtractor
from src.data.data_loader import DataLoader

from src.watchdog import WatchdogLogger

# -------------------------
# Main ETL Process
# -------------------------
def run_etl(cfg: dict):
    start_time = time.time()

    with DBConnector(cfg) as conn:
        cur = conn.cursor()

        # Extract data from the DB
        extractor = DataExtractor(conn, cfg)
        df = extractor.extract()

        # Wrangling data
        wrangler = DataWrangler(cfg.get("wrangling", []), dry_run=cfg.get("dry_run", False))
        df = wrangler.apply(df)

        # Filtering data
        filterer = DataFilter(cfg.get("filtering", []), dry_run=cfg.get("dry_run", False))
        df = filterer.apply(df)

        # Loading data
        loader = DataLoader(cfg)
        loader.load(df)

        # Watch dog
        watchdog = WatchdogLogger(conn, cfg)
        watchdog.log(len(df), start_time)

        # Final commit
        conn.commit()

# -------------------------
# Entrypoint
# -------------------------
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Run ETL with given config file")
    parser.add_argument(
        "-c", "--config",
        type=str,
        required=True,
        help="Path to config JSON file"
    )
    args = parser.parse_args()

    cfg = load_config(args.config)

    cfg = load_config("config/config.json")
    setup_logging(cfg.get("log_level", "INFO"))
    run_etl(cfg)
