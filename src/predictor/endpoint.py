from datetime import datetime
from typing import TYPE_CHECKING

from flask import Blueprint, jsonify, request

from predictor.preprocess.mapping import MAPPING
from worklogger import get_logger

if TYPE_CHECKING:
    from .workflow.workflow import Workflow

logger = get_logger(__name__)


class WorkflowRequestHandler:
    workflow: "Workflow"
    blueprint: Blueprint

    def __init__(self, workflow: "Workflow"):
        self.workflow = workflow
        self.blueprint = Blueprint(self.workflow.name, __name__, url_prefix=f"/{self.workflow.name}")
        self.register_paths()

    def register_paths(self):
        @self.blueprint.route("/predict/<string:destination>/", methods=["GET"])
        def func(destination):
            if destination not in self.workflow.nodes:
                return jsonify({"status": "bad destination"}), 404

            if not (json := request.get_json(silent=True)):
                logger.debug("request is missing json data")
                raise KeyError("json")

            time = json.get("time", None)

            done_dict = {}
            processing_dict = {}
            parameters_dict = {}

            for done, time in json["done"].items():
                if not isinstance(done, str):
                    raise TypeError("done", done)

                if done not in self.workflow.nodes:
                    logger.warning(f"unknown task {done}")
                    continue

                if not isinstance(time, (int, str, float)):
                    raise TypeError(f"done:{done}", time)

                done_dict[done] = datetime.fromtimestamp(int(time))

            for processing, time in json["processing"].items():
                if not isinstance(processing, str):
                    raise TypeError("processing", processing)

                if processing not in self.workflow.nodes:
                    logger.warning(f"unknown task {done}")
                    continue

                if not isinstance(time, (int, str, float)):
                    raise TypeError(f"processing:{processing}", time)

                processing_dict[done] = datetime.fromtimestamp(int(time))

            # im not sure how we will receive those parameters, so for now ill assume dictionary {param: value, ...}
            for parameter, value in json["parameters"].items():
                if not isinstance(parameter, str):
                    raise TypeError("parameter", parameter)

                if not isinstance(value, (str, int, float)):
                    raise TypeError(f"parameter: {parameter}", value)

                if parameter not in MAPPING:
                    logger.warning(f"unknown run parameter '{parameter}'")
                else:
                    # also have to map ever parameter, and then pass it into predict
                    parameters_dict.update(MAPPING[parameter](parameter, value))

            return jsonify(self.workflow.predict(destination, done_dict, processing_dict, parameters_dict, time)), 200

        def handle_key_missing(e: KeyError):
            logger.error("Key missing", exc_info=e)
            return jsonify({"status": "error", "missing": e.args[0]}), 415

        self.blueprint.register_error_handler(KeyError, handle_key_missing)

        def handle_bad_type(e: TypeError):
            logger.error("Bad type of a parameter", exc_info=e)
            return jsonify({"status": "error", "key": e.args}), 415

        self.blueprint.register_error_handler(TypeError, handle_bad_type)

        def handle_value_error(e: ValueError):
            logger.error("Bad value type", exc_info=e)
            return jsonify({"status": "error"}), 415

        self.blueprint.register_error_handler(ValueError, handle_value_error)

        return func
