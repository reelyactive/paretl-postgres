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

            col, op, val = step["col"], step["op"], step["val"]
            before = len(df)
   
            if not self.dry_run:
                if op == "==":   df = df[df[col] == val]
                elif op == "!=": df = df[df[col] != val]
                elif op == ">":  df = df[df[col] >  val]
                elif op == ">=": df = df[df[col] >= val]
                elif op == "<":  df = df[df[col] <  val]
                elif op == "<=": df = df[df[col] <= val]
                elif op.lower() == "in":  df = df[df[col].isin(val)]
                else:
                    logging.error(f"[Filter] Unsupported operator: {op}")
                    raise ValueError(f"Unsupported filter operator: {op}")

            after = len(df)
            logging.info(f"[Filter] Filter on {col} {op} {val}: {before} → {after} ({(after - before) / before:.1%})")

        logging.info(f"[Filter] Output shape: {df.shape}")
        return df