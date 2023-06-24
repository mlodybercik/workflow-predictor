# TODO: implement gunicorn logger for logging requests

import json
import logging
import logging.config
import os
import typing as T
from pathlib import Path

from flask import Flask

LOGGING_CONFIG_LOCATION = os.environ.get("LOGGING_CONFIG_LOCATION", False)
LOGGING_LEVEL = os.environ.get("LOGGING_LEVEL", "DEBUG").upper()

logger_set_up: bool = False


def get_logger(name: str, level: T.Optional[str] = None) -> logging.Logger:
    global logger_set_up
    logging_level = LOGGING_LEVEL

    if not logger_set_up:
        path = Path(LOGGING_CONFIG_LOCATION if LOGGING_CONFIG_LOCATION else __file__).parent.parent / "logging.json"
        if not path.absolute().exists():
            raise ValueError(f"logging config doesn't exist '{path}'")

        with open(path) as file:
            logging.config.dictConfig(json.loads(file.read()))

    if level:
        logging_level = level

    logger = logging.getLogger(name)
    logger.setLevel(logging_level)
    return logger


def set_up_flask_logger(app: Flask):
    formatter = logging.Formatter("%(message)s")
    [handler.setFormatter(formatter) for handler in app.logger.handlers]
