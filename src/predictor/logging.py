# TODO: implement gunicorn logger for logging requests

import json
import logging
import logging.config
import os
from pathlib import Path
from typing import Optional

LOGGING_CONFIG_LOCATION = os.environ.get("LOGGING_CONFIG_LOCATION", False)
LOGGING_LEVEL = os.environ.get("LOGGING_LEVEL", "DEBUG").upper()

logger: logging.Logger = None


def init_logger(log_level: Optional[str] = None) -> logging.Logger:
    global logger

    if not log_level:
        log_level = LOGGING_LEVEL

    path = Path(LOGGING_CONFIG_LOCATION if LOGGING_CONFIG_LOCATION else __file__).parent.parent / "logging.json"
    if not path.absolute().exists():
        raise ValueError(f"logging config doesn't exist '{path}'")

    with open(path) as file:
        logging.config.dictConfig(json.loads(file.read()))
    logger = logging.getLogger(__name__)

    logger.setLevel(log_level)
    return logger
