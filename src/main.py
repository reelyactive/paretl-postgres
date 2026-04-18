import json
import logging
import time
import psutil
import psycopg2
import pandas as pd
import argparse

from sqlalchemy import engine, create_engine
from datetime import datetime

from src.logger_setup import setupLogging
from src.config_loader import loadConfig
from src.db_connector import DBConnector

from src.data.data_wrangler import DataWrangler
from src.data.data_filter import DataFilter
from src.data.data_extractor import DataExtractor
from src.data.data_loader import DataLoader

from src.watchdog import WatchdogLogger

# -------------------------
# Main ETL Process
# -------------------------
def runETL(cfg: dict):
    startTime = time.time()

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

        # Watch dog
        watchdog = WatchdogLogger(conn, cfg)
        watchdogId = watchdog.log(df, startTime)

        # Loading data
        loader = DataLoader(cfg)
        loader.load(df, watchdogId)

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

    cfg = loadConfig(args.config)
    #cfg = load_config("config/config.json")
    setupLogging(cfg.get("log_level", "INFO"))
    runETL(cfg)
    logging.info("Process completed.")
    logging.info("Yippee-ki-yay.")

    

