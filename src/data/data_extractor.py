import sys
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
            minTs, maxTs = cur.fetchone()
            logging.info(f"[Extractor] Available time window between {minTs} and {maxTs}")

        # Try to read start and end from config
        startTs = self.cfg.get("start_ts")  # expect ISO string or None
        endTs = self.cfg.get("end_ts")

	# The ETL is either run for a (start;end) time window
	# Or for a (now;now-frequency) time window
        if startTs and endTs:
            # Parse strings to datetime if needed
            startTs = datetime.fromisoformat(startTs) if isinstance(startTs, str) else startTs
            endTs = datetime.fromisoformat(endTs) if isinstance(endTs, str) else endTs
        else:
            # Fallback: use frequency
            freq_minutes = int(self.cfg.get("frequency_minutes", 60))
            endTs = datetime.now()
            startTs = endTs - timedelta(minutes=freq_minutes)

        # Construct and execute query        
        receivers = self.cfg['receivers_id']  # e.g. [1, 2, 3]
        placeHolders = ",".join(["%s"] * len(receivers))
        query = f"""
            SELECT 
            timestamp,
            raddec->>'transmitterId' AS transmitterid,
            raddec->>'receiverId' AS receiverid,
            raddec->>'rssi' AS rssi,
            raddec->>'numberofdecodings' AS numberofdecodings
            FROM {self.cfg['source_table']}
            WHERE timestamp BETWEEN %s AND %s
            AND raddec->>'receiverId' IN ({placeHolders})
        """
        
        params = [startTs, endTs] + receivers
      
        with self.conn.cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()
            colnames = [desc[0] for desc in cur.description]

        df = pd.DataFrame(rows, columns=colnames)
        
        if len(df) == 0:
            print("Extraction from database results in an empty table")
            sys.exit(1)
        
        # Check that the columns used later are all available
        required_cols = {"timestamp", "rssi", "transmitterid", "receiverid", "numberofdecodings"}
        actual_cols = set(df.columns)
        missing = required_cols - actual_cols
        if missing:
            print(f"Error: Missing required columns in DataFrame: {', '.join(missing)}")
            print("Expected columns derived from raddec: timestamp, rssi, transmitterid, receiverid.")
            sys.exit(1) # Exit the script with an error code
        
        
        logging.info(f"[Extractor] Extracted for event {self.cfg['event_name']} {len(df)} rows from {self.cfg['source_table']} "
                     f"between {startTs} and {endTs} for the receivers {receivers}")
        return df
