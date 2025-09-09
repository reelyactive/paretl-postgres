import psycopg2
import sqlite3
# you can add other imports here (e.g., mysql.connector, pyodbc, etc.)

class DBConnector:
    """
    Generic context manager for database connections.
    The type of DB is defined in the config JSON under 'db_type'.
    Example:
        with DBConnector(cfg) as conn:
            cur = conn.cursor()
            cur.execute("SELECT 1;")
    """

    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.conn = None

    def __enter__(self):
        db_type = self.cfg.get("db_type", "").lower()

        if db_type == "postgresql":
            self.conn = psycopg2.connect(
                host=self.cfg["db_host"],
                port=self.cfg["db_port"],
                user=self.cfg["db_user"],
                password=self.cfg["db_pass"],
                dbname=self.cfg["db_name"]
            )

        elif db_type == "sqlite":
            self.conn = sqlite3.connect(self.cfg["db_name"])

        else:
            raise ValueError(f"Unsupported db_type: {db_type}")

        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            try:
                self.conn.close()
            except Exception as e:
                raise RuntimeError(f"Failed to close DB connection: {e}")
