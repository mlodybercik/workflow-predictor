from json import load as json_load
from pathlib import Path
from typing import TYPE_CHECKING, Dict

from yaml import CLoader
from yaml import load as yaml_load

from .model import BlankModel
from .types import Loader
from .utils import list_dir
from .workflow import Workflow

if TYPE_CHECKING:
    from .model import ModelBank, Model

from . import logger

logger = logger.getChild("loader")


class WorkflowLoader(Loader):
    model_bank: "ModelBank"

    def __init__(self, location: Path, model_bank: "ModelBank"):
        self.model_bank = model_bank
        super().__init__(location)

    @staticmethod
    def filter_file(path: Path) -> bool:
        return path.name.endswith("flow.yml")

    def load(self, file_path: Path) -> "Workflow":
        flow_name = file_path.name.removesuffix(".yml")
        logger.info(f"Loading {flow_name}")
        with open(file_path) as file:
            workflow_dict = yaml_load(file, CLoader)

        connections = []
        nodes = set()

        for job_dict in workflow_dict["workflows"][0]["jobs"]:
            if (
                (job := job_dict.get("job", None))
                # job is a normal kind of a job
                or (job := job_dict.get("nop", None))
                # nop is used to connect multiple nodes back to one
                or (job := job_dict.get("jobReference", None))
                # jobReference is a reference to node in other workflow
            ):
                name = job.get("name")
                nodes.add(name)
                for precondition in job.get("precondition", []):
                    nodes.add(precondition)
                    connections.append((precondition, name))
            else:
                logger.debug("job_dict yielded unknown job type")
        return Workflow(flow_name, nodes, connections, self.model_bank)

    def load_all(self) -> Dict[str, "Workflow"]:
        logger.debug("Attempting to load all workflows")
        ret = dict()
        for file_path in self.filter_files(list_dir(self.location)):
            flow_name = file_path.name.removesuffix(".yml")
            ret[flow_name] = self.load(file_path)
        return ret


class ModelLoader(Loader):
    def load(self, name: str):
        logger.warning("Attempting to load single model is not supported right now.")
        return BlankModel(name, 1)

    def filter_file(self, file):
        return True

    def load_all(self) -> Dict[str, "Model"]:
        logger.debug("Attempting to load all models")
        # TODO: this is temporary until we create some kind of model export system.
        ret = dict()
        with open(self.location / "means.json") as file:
            models = json_load(file)

        for name, mean in models.items():
            ret[name] = BlankModel(name, mean)
        return ret
