import logging
import pandas as pd
from sqlalchemy import create_engine

class DataLoader:
    """
    Handles loading a DataFrame into a database table.
    Appends to existing table or creates it if missing.
    """
    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.engine = self._create_engine()

    def _create_engine(self):
        db_type = self.cfg.get("db_type", "postgresql").lower()

        if db_type == "postgresql":
            user = self.cfg["db_user"]
            password = self.cfg["db_pass"]
            host = self.cfg["db_host"]
            port = self.cfg["db_port"]
            db = self.cfg["db_name"]
            url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
        elif db_type == "sqlite":
            db = self.cfg["db_name"]
            url = f"sqlite:///{db}"
        else:
            raise ValueError(f"Unsupported db_type: {db_type}")

        return create_engine(url)

    def load(self, df: pd.DataFrame):
        table = self.cfg["target_table"]
        inspector = inspect(self.engine)
        table_exists = table in inspector.get_table_names()

        if not table_exists:
            logging.info(f"[Loader] Table '{table}' does not exist. It will be created.")
        else:
            logging.info(f"[Loader] Table '{table}' exists. Appending data.")

        df.to_sql(table, self.engine, if_exists="append", index=False)