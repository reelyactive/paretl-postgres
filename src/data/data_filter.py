import pandas as pd
import logging

class DataFilter:
    """
    Apply row-level filtering:
    - filter by comparison operators
    Supports dry_run mode for logging only.
    """
    def __init__(self, steps: list[dict], dry_run: bool = False):
        self.steps = steps
        self.dry_run = dry_run

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        logging.info(f"[Filter] Input shape: {df.shape}")
        for step in self.steps:
            action = step.get("name", "").lower()
            logging.info(f"[Filter] Applying step: {action}")

            if action == "filter":
                col, op, val = step["col"], step["op"], step["val"]
                before = len(df)

                if not self.dry_run:
                    if op == "==":   df = df[df[col] == val]
                    elif op == "!=": df = df[df[col] != val]
                    elif op == ">":  df = df[df[col] >  val]
                    elif op == ">=": df = df[df[col] >= val]
                    elif op == "<":  df = df[df[col] <  val]
                    elif op == "<=": df = df[df[col] <= val]
                    else:
                        logging.error(f"[Filter] Unsupported operator: {op}")
                        raise ValueError(f"Unsupported filter operator: {op}")

                logging.info(f"[Filter] Would filter on {col} {op} {val} → {before - len(df)} rows removed")

            else:
                logging.warning(f"[Filter] Unknown action skipped: {action}")
        logging.info(f"[Filter] Output shape: {df.shape}")
        return df