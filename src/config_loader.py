import os
import json

def load_config(path: str) -> dict:
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
    required_keys = [
        "frequency_minutes","wrangling", "filtering","dry_run",
        "db_type", "db_host", "db_port", "db_user", "db_pass", "db_name",
        "source_table", "target_table", "watchdog_table"
    ]
    missing = [k for k in required_keys if k not in cfg]
    if missing:
        raise KeyError(f"Missing required config keys: {missing}")

    return cfg
