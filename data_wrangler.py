import pandas as pd
import logging

class DataWrangler:
    """
    Apply general cleaning and transformations:
    - drop_nulls
    - rename
    - select_columns
    - add_column
    Supports dry_run mode for logging only.
    """
    def __init__(self, steps: list[dict], dry_run: bool = False):
        self.steps = steps
        self.dry_run = dry_run

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        logging.info(f"[Wrangler] Input shape: {df.shape}")
        for step in self.steps:
            action = step.get("name", "").lower()
            logging.info(f"[Wrangler] Applying step: {action}")

            if action == "drop_nulls":
                before = len(df)
                if not self.dry_run:
                    df = df.dropna()
                logging.info(f"[Wrangler] Would drop {before - len(df)} rows with nulls")

            elif action == "rename":
                mapping = step.get("mapping", {})
                if not self.dry_run:
                    df = df.rename(columns=mapping)
                logging.info(f"[Wrangler] Would rename columns: {mapping}")

            elif action == "select_columns":
                cols = step.get("columns", [])
                if not self.dry_run:
                    df = df[cols]
                logging.info(f"[Wrangler] Would select columns: {cols}")

            elif action == "add_column":
                col, val = step["new_col"], step["value"]
                if not self.dry_run:
                    df[col] = val
                logging.info(f"[Wrangler] Would add column '{col}' with value {val}")

            else:
                logging.warning(f"[Wrangler] Unknown action skipped: {action}")
        logging.info(f"[Wrangler] Output shape: {df.shape}")
        return df