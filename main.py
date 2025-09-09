import json
import logging
import time
import psutil
import psycopg2
import pandas as pd
from datetime import datetime

from logger_setup import setup_logging
from config_loader import load_config
from db_connector import DBConnector
from data_wrangler import DataWrangler
from data_filter import DataFilter
from data_extractor import DataExtractor
from data_loader import DataLoader
from watchdog import WatchdogLogger

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
    cfg = load_config("config.json")
    setup_logging(cfg.get("log_level", "INFO"))
    run_etl(cfg)
