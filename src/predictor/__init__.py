import json
import logging
import logging.config
import os
from pathlib import Path

from flask import Flask

from .predictor import Predictor

logger: logging.Logger = None


LOGGING_CONFIG_LOCATION = os.environ.get("LOGGING_CONFIG_LOCATION", False)
LOGGING_LEVEL = os.environ.get("LOGGING_LEVEL", "DEBUG").upper()

GRAPH_DEFINITIONS_LOCATION = os.environ.get("GRAPH_DEFINITIONS_LOCATION", "/tmp/workflows/")
MODEL_DEFINITIONS_LOCATION = os.environ.get("MODEL_DEFINITIONS_LOCATION", "/tmp/models/")


def init_logger(log_level: str) -> logging.Logger:
    global logger

    path = Path(LOGGING_CONFIG_LOCATION if LOGGING_CONFIG_LOCATION else __file__).parent.parent / "logging.json"
    if not path.absolute().exists():
        raise ValueError(f"logging config doesn't exist '{path}'")

    with open(path) as file:
        logging.config.dictConfig(json.loads(file.read()))
    logger = logging.getLogger(__name__)

    logger.setLevel(log_level)
    return logger


def get_app() -> Flask:
    init_logger(LOGGING_LEVEL)
    logger.info("Creating app...")
    app = Flask(__name__)

    graph_location = Path(GRAPH_DEFINITIONS_LOCATION)
    model_location = Path(MODEL_DEFINITIONS_LOCATION)

    predictor = Predictor(model_location, graph_location)
    predictor.load_blueprints(app)
    app.predictor = predictor

    return app
