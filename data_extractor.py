import pandas as pd
import logging
from datetime import datetime, timedelta

class DataExtractor:
    """
    Handles data extraction from a database.
    Computes dynamic query window from frequency_minutes in config.
    """
    def __init__(self, conn, cfg: dict):
        self.conn = conn
        self.cfg = cfg

    def extract(self) -> pd.DataFrame:
        freq_minutes = int(self.cfg.get("frequency_minutes", 60))
        end_ts = datetime.utcnow()
        start_ts = end_ts - timedelta(minutes=freq_minutes)

        query = f"""
            SELECT * FROM {self.cfg['source_table']}
            WHERE timestamp BETWEEN %s AND %s
        """

        with self.conn.cursor() as cur:
            cur.execute(query, (start_ts, end_ts))
            rows = cur.fetchall()
            colnames = [desc[0] for desc in cur.description]

        df = pd.DataFrame(rows, columns=colnames)
        logging.info(f"[Extractor] Extracted {len(df)} rows from {self.cfg['source_table']} "
                     f"between {start_ts} and {end_ts}")
        return df