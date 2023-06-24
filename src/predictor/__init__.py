import os
from pathlib import Path

from flask import Flask

from worklogger import get_logger, set_up_flask_logger

from .predictor import Predictor

logger = get_logger(__name__)

GRAPH_DEFINITIONS_LOCATION = os.environ.get("GRAPH_DEFINITIONS_LOCATION", "/tmp/workflows/")
MODEL_DEFINITIONS_LOCATION = os.environ.get("MODEL_DEFINITIONS_LOCATION", "/tmp/models/")


def get_app() -> Flask:
    logger.info("Creating app...")
    app = Flask(__name__)

    set_up_flask_logger(app)

    graph_location = Path(GRAPH_DEFINITIONS_LOCATION)
    model_location = Path(MODEL_DEFINITIONS_LOCATION)

    predictor = Predictor(model_location, graph_location)
    predictor.load_blueprints(app)
    app.predictor = predictor

    return app
