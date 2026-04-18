import pandas as pd
import logging
from tabulate import tabulate

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
        
        logging.info(f"[Wrangler] Data shape:\n" + tabulate(
                df.head(3),
                headers="keys",
                tablefmt="psql",
                showindex=False
            ))
        
        # Convert timestamp to datetime
        logging.info(f"[Wrangler] Converting timestamp to datetime...")
        df["timestamp"] = pd.to_datetime(df["timestamp"], format="%b %d, %Y @ %H:%M:%S.%f")
        
        # Ensure RSSI is integer
        logging.info(f"[Wrangler] Ensuring RSSI is integer...")
        df["rssi"] = df["rssi"].astype(int)
        
        # Ensure RSSI is integer
        logging.info(f"[Wrangler] Ensuring numberofdecodings is integer...")
        df["numberofdecodings"] = df["numberofdecodings"].astype(int)

        # Ensure IDs are strings
        logging.info(f"[Wrangler] Ensuring IDs are strings...") 
        df["transmitterid"] = df["transmitterid"].astype(str)
        df["receiverid"] = df["receiverid"].astype(str)
         
        # Number of measurements per transmitter
        logging.info(f"[Wrangler] Calculating number of measurements per transmitter...") 
        dfMetrics = (
            df.groupby("transmitterid")
            .agg(
                nb_counts=("numberofdecodings", "sum"),
                min_time=("timestamp", "min"),
                max_time=("timestamp", "max"),
                max_rssi=("rssi", "max"))
            .reset_index()  
        )

        # Calculate max-min time for each transmitter
        logging.info(f"[Wrangler] Calculating time window and max RSSI per transmitter...") 
        dfMetrics["duration_seconds"] = (dfMetrics["max_time"] - dfMetrics["min_time"]).dt.total_seconds()
        df = df.merge(dfMetrics[["transmitterid", "duration_seconds", "max_rssi", "nb_counts"]], on="transmitterid", how="left")
        del dfMetrics
        

        # Second character in the mac address
        logging.info(f"[Wrangler] Extracting second character of transmitterId...") 
        unique_ids = df["transmitterid"].unique().tolist()
        
        dfMetrics = pd.DataFrame(
            [list(uid) for uid in unique_ids], 
            columns=[f"char_{i}" for i in range(len(unique_ids[0]))]
        )
        dfMetrics = dfMetrics[["char_1"]]
        dfMetrics = dfMetrics.rename(columns={"char_1": "digit_2"})
        privateSet = {"a", "e", "2", "6"}
        dfMetrics["is_private"] = dfMetrics["digit_2"].isin(privateSet)
        # remove digit_2 column as we have the private flag now
        dfMetrics = dfMetrics.drop(columns=["digit_2"])
        dfMetrics["transmitterid"] = unique_ids
        del unique_ids
        df = df.merge(dfMetrics, on="transmitterid", how="left")
        del dfMetrics  
            
        logging.info(f"[Wrangler] Data shape:\n" + tabulate(
                df.head(3),
                headers="keys",
                tablefmt="psql",
                showindex=False
            ))
        
        return df
