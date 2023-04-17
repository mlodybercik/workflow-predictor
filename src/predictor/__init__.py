import json
import logging
import logging.config
import os
from pathlib import Path

from flask import Flask

from . import workflow

logger: logging.Logger = None


LOGGING_CONFIG_LOCATION = os.environ.get("LOGGING_CONFIG_LOCATION", False)
LOGGING_LEVEL = os.environ.get("LOGGING_LEVEL", "DEBUG").upper()


def init_logger() -> logging.Logger:
    global logger

    path = Path(LOGGING_CONFIG_LOCATION if LOGGING_CONFIG_LOCATION else __file__).parent.parent / "logging.json"
    if not path.absolute().exists():
        raise ValueError(f"logging config doesn't exist '{path}'")

    with open(path) as file:
        logging.config.dictConfig(json.loads(file.read()))
    logger = logging.getLogger(__name__)

    logger.setLevel(LOGGING_LEVEL)
    return logger


def hello():
    return "hello world", 200


def get_app() -> Flask:
    init_logger()
    logger.info("Creating app...")
    app = Flask(__name__)

    for blueprint in [workflow.predictor]:
        app.register_blueprint(blueprint)

    return app
