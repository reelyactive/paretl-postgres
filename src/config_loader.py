import os
import json

def loadConfig(path: str) -> dict:
    """
    Load and validate configuration from a JSON file.
    Returns a dictionary with configuration values.
    """

    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(path, "r") as f:
        try:
            cfg = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in {path}: {e}")

    # Minimal required keys
    requiredKeys = [
        "filtering","dry_run","receivers_id","event_name",
        "db_type", "db_host", "db_port", "db_user", "db_pass", "db_name",
        "source_table", "target_table", "watchdog_table"
    ]
    missing = [k for k in requiredKeys if k not in cfg]
    if missing:
        raise KeyError(f"Missing required config keys: {missing}")

    # Check frequency vs start/end
    freq = cfg.get("frequency_minutes")
    startTs = cfg.get("start_ts")
    endTs = cfg.get("end_ts")

    if not freq and not (startTs and endTs):
        missingTimeKeys = ["frequency_minutes or (start_ts and end_ts)"]
        missing.extend(missingTimeKeys)

    if freq and (startTs or endTs):
        raise KeyError("Provide either 'frequency_minutes' OR both 'start_ts' and 'end_ts', not both.")

    if missing:
        raise KeyError(f"Missing required config keys: {missing}")

    return cfg
