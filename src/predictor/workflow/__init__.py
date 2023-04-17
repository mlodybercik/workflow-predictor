import logging

from flask.blueprints import Blueprint

logger = logging.getLogger(__name__)
predictor = Blueprint("predictor", __name__)


@predictor.get("/hello")
def hello_world():
    return "<h1>hello world</h1>"
