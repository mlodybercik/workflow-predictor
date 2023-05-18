from typing import TYPE_CHECKING

from flask import Blueprint, jsonify

if TYPE_CHECKING:
    from .workflow.workflow import Workflow


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
            if destination in self.workflow.nodes:
                return jsonify(list(self.workflow.find_all_paths(self.workflow.graph, destination)))
            return jsonify({"status": "D:"}), 404

        return func
