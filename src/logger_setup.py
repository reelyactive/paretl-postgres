import logging

# Configure logging
def setup_logging(level: str = "INFO"):
    """
    Configure application-wide logging.
    """
    valid_levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }

    chosen_level = valid_levels.get(level.upper())
    if chosen_level is None:
        raise ValueError(
            f"Invalid log level '{level}'. Must be one of: {list(valid_levels.keys())}"
        )

    logging.basicConfig(
        level=chosen_level,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
    logging.info(f"Logging initialized at level {level.upper()}")
