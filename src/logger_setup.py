import logging

# Configure logging
def setupLogging(level: str = "INFO"):
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

    chosenLevel = valid_levels.get(level.upper())
    if chosenLevel is None:
        raise ValueError(
            f"Invalid log level '{level}'. Must be one of: {list(valid_levels.keys())}"
        )

    logging.basicConfig(
        level=chosenLevel,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
    logging.info(f"Logging initialized at level {level.upper()}")
