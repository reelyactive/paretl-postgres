import time
import logging
from datetime import datetime
import psutil
from sqlalchemy import create_engine, inspect, text
from tabulate import tabulate
import pandas as pd

class WatchdogLogger:
    """
    Logs ETL statistics to a watchdog table in the database.
    Stats include: timestamp, number of rows, duration, CPU, memory usage.
    """
    def __init__(self, conn, cfg: dict):
        self.conn = conn
        self.cfg = cfg
        self.table = cfg.get("watchdog_table", "etl_watchdog")  # default fallback
        
        # Check if table exists
        with self.conn.cursor() as cur:
            cur.execute(f"SELECT to_regclass('public.{self.table}')")
            exists = cur.fetchone()[0] is not None

        # Create table if missing
        if not exists:
            with self.conn.cursor() as cur:
                cur.execute(f"""
                    CREATE TABLE {self.table} (
                        id SERIAL PRIMARY KEY,
                        event_name VARCHAR(255),
                        ts TIMESTAMP NOT NULL,
                        rows INTEGER NOT NULL,
                        duration_sec NUMERIC,
                        cpu_percent NUMERIC,
                        memory_mb NUMERIC,
                        n_transmitters INTEGER,
                        n_transmitters_per_day TEXT,
                        median_duration_seconds NUMERIC,
                        mean_duration_seconds NUMERIC,
                        std_duration_seconds NUMERIC
                    )
                """)
                self.conn.commit()
        
    def log(self, df: pd.DataFrame, start_time: float):
        
        # Number of rows processed
        rowCount = len(df)
        # Duration of the ETL process
        duration = time.time() - start_time
        # Number of unique transmitters
        nTransmitters = df['transmitterid'].nunique()
        # convert the timestamp to date
        df['date'] = df['timestamp'].dt.date
        # Number of unique transmitters per day
        nTransmittersPerDay = df.groupby('date')['transmitterid'].nunique().to_dict()
        # Gather in a string
        nTransmittersPerDay = ", ".join([f"{k}: {v}" for k, v in nTransmittersPerDay.items()])
        # Median time window
        medianTimeWindow = df['duration_seconds'].median()
        # Mean time window
        meanTimeWindow = df['duration_seconds'].mean() 
        # standard deviation of time window
        stdTimeWindow = df['duration_seconds'].std()
        
        stats = {
            "event_name": self.cfg.get("event_name", "unknown_event"),
            "ts": datetime.now().replace(microsecond=0),   # remove microseconds
            "rows": rowCount,
            "duration_sec": round(duration, 1),            # 2 decimal places
            "cpu_percent": round(psutil.cpu_percent(), 1), # 1 decimal place
            "memory_mb": round(psutil.virtual_memory().used / (1024 * 1024)),
            "n_transmitters": nTransmitters,
            "n_transmitters_per_day": nTransmittersPerDay,
            "median_duration_seconds": float(round(medianTimeWindow, 1)),
            "mean_duration_seconds": float(round(meanTimeWindow, 1)),
            "std_duration_seconds": float(round(stdTimeWindow, 1)),
        }

        try:
            
            # Save locally as CSV
            timestampStr = stats["ts"].strftime("%Y-%m-%d_%Hh%M")
            filename = f"paretl_{stats['event_name']}_{timestampStr}.csv"
            filename = filename.replace(" ", "_")

            # Save
            dfStats = pd.DataFrame([stats])
            dfStats.to_csv(filename, index=False)
            logging.info(f"[Watchdog] ETL stats saved in {filename}")

            with self.conn.cursor() as cur:
                cur.execute(
                    f"INSERT INTO {self.cfg['watchdog_table']} "
                    f"(event_name, ts, rows, duration_sec, cpu_percent, memory_mb, n_transmitters, n_transmitters_per_day, median_duration_seconds, mean_duration_seconds, std_duration_seconds) "
                    f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id",
                    ( stats["event_name"],
                    stats["ts"], 
                    stats["rows"],
                    stats["duration_sec"],
                    stats["cpu_percent"],
                    stats["memory_mb"],
                    stats["n_transmitters"],
                    stats["n_transmitters_per_day"],
                    stats["median_duration_seconds"],
                    stats["mean_duration_seconds"],
                    stats["std_duration_seconds"])
                )
                watchdog_id = cur.fetchone()[0]
            self.conn.commit()            
            
            logging.info(f"[Watchdog] Logged ETL stats:\n" + tabulate(stats.items(), headers=["Metric", "Value"], tablefmt="pretty"))
    
            return watchdog_id
        except Exception as e:
            logging.error(f"[Watchdog] Failed to log stats: {e}")
            self.conn.rollback()
