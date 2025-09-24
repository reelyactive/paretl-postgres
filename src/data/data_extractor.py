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
        # Determine time window for data extraction 

        with self.conn.cursor() as cur:
            cur.execute(f"SELECT MIN(timestamp), MAX(timestamp) FROM {self.cfg['source_table']}")
            min_ts, max_ts = cur.fetchone()
            logging.info(f"[Extractor] Available time window between {min_ts} and {max_ts}")

        # Try to read start and end from config
        start_ts = self.cfg.get("start_ts")  # expect ISO string or None
        end_ts = self.cfg.get("end_ts")

        if start_ts and end_ts:
            # Parse strings to datetime if needed
            start_ts = datetime.fromisoformat(start_ts) if isinstance(start_ts, str) else start_ts
            end_ts = datetime.fromisoformat(end_ts) if isinstance(end_ts, str) else end_ts
        else:
            # Fallback: use frequency
            freq_minutes = int(self.cfg.get("frequency_minutes", 60))
            end_ts = datetime.now()
            start_ts = end_ts - timedelta(minutes=freq_minutes)

        # Construct and execute query        
        receivers = self.cfg['receivers_id']  # e.g. [1, 2, 3]
        placeholders = ",".join(["%s"] * len(receivers))
        query = f"""
            SELECT * FROM {self.cfg['source_table']}
            WHERE timestamp BETWEEN %s AND %s
            AND receiverid IN ({placeholders})
        """
        params = [start_ts, end_ts] + receivers

        with self.conn.cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()
            colnames = [desc[0] for desc in cur.description]

        df = pd.DataFrame(rows, columns=colnames)
        logging.info(f"[Extractor] Extracted for event {self.cfg['event_name']} {len(df)} rows from {self.cfg['source_table']} "
                     f"between {start_ts} and {end_ts} for the receivers {receivers}")
        return df