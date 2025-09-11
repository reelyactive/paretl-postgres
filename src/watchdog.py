import time
import logging
from datetime import datetime
import psutil
from sqlalchemy import create_engine, inspect, text
from tabulate import tabulate

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
                        ts TIMESTAMP NOT NULL,
                        rows INTEGER NOT NULL,
                        duration_sec NUMERIC,
                        cpu_percent NUMERIC,
                        memory_mb NUMERIC
                    )
                """)
                self.conn.commit()
        
    def log(self, row_count: int, start_time: float):
        duration = time.time() - start_time
        stats = {
            "ts": datetime.now().replace(microsecond=0),   # remove microseconds
            "rows": row_count,
            "duration_sec": round(duration, 1),            # 2 decimal places
            "cpu_percent": round(psutil.cpu_percent(), 1), # 1 decimal place
            "memory_mb": round(psutil.virtual_memory().used / (1024 * 1024))
        }

        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    f"INSERT INTO {self.cfg['watchdog_table']} "
                    f"(ts, rows, duration_sec, cpu_percent, memory_mb) "
                    f"VALUES (%s, %s, %s, %s, %s) RETURNING id",
                    (stats["ts"], stats["rows"], stats["duration_sec"],
                     stats["cpu_percent"], stats["memory_mb"])
                )
                watchdog_id = cur.fetchone()[0]
            self.conn.commit()            
            
            logging.info(f"[Watchdog] Logged ETL stats:\n" + tabulate(stats.items(), headers=["Metric", "Value"], tablefmt="pretty"))
    
            return watchdog_id
        except Exception as e:
            logging.error(f"[Watchdog] Failed to log stats: {e}")
            self.conn.rollback()
