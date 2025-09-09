import time
import logging
from datetime import datetime
import psutil

class WatchdogLogger:
    """
    Logs ETL statistics to a watchdog table in the database.
    Stats include: timestamp, number of rows, duration, CPU, memory usage.
    """
    def __init__(self, conn, cfg: dict):
        self.conn = conn
        self.cfg = cfg

    def log(self, row_count: int, start_time: float):
        duration = time.time() - start_time
        stats = {
            "ts": datetime(),
            "rows": row_count,
            "duration_sec": duration,
            "cpu_percent": psutil.cpu_percent(),
            "mem_mb": psutil.virtual_memory().used / (1024 * 1024)
        }

        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    f"INSERT INTO {self.cfg['watchdog_table']} "
                    f"(ts, rows, duration_sec, cpu_percent, mem_mb) "
                    f"VALUES (%s, %s, %s, %s, %s)",
                    (stats["ts"], stats["rows"], stats["duration_sec"],
                     stats["cpu_percent"], stats["mem_mb"])
                )
            self.conn.commit()
            logging.info(f"[Watchdog] Logged ETL stats: {stats}")
        except Exception as e:
            logging.error(f"[Watchdog] Failed to log stats: {e}")
            self.conn.rollback()
