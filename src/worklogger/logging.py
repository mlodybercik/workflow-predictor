# TODO: implement gunicorn logger for logging requests

import json
import logging
import logging.config
import os
from pathlib import Path

LOGGING_CONFIG_LOCATION = os.environ.get("LOGGING_CONFIG_LOCATION", False)
LOGGING_LEVEL = os.environ.get("LOGGING_LEVEL", "DEBUG").upper()

logger_set_up: bool = False


def get_logger(name: str) -> logging.Logger:
    global logger_set_up

    if not logger_set_up:
        path = Path(LOGGING_CONFIG_LOCATION if LOGGING_CONFIG_LOCATION else __file__).parent.parent / "logging.json"
        if not path.absolute().exists():
            raise ValueError(f"logging config doesn't exist '{path}'")

        with open(path) as file:
            logging.config.dictConfig(json.loads(file.read()))

    logger = logging.getLogger(name)
    logger.setLevel(LOGGING_LEVEL)
    return logger
