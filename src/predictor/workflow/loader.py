from pathlib import Path
from typing import Dict

from yaml import CLoader
from yaml import load as yaml_load

from serialize.model import ModelSerializer
from worklogger import get_logger

from .model import ModelBank, TFModel
from .types import Loader
from .utils import list_dir
from .workflow import Workflow

logger = get_logger(__name__)


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
        with ModelSerializer(self.location / f"{name}.wfp", "r") as archive:
            model, meta, inv_func = archive.load_model_from_zip()
        return TFModel(meta, model, inv_func)

    @staticmethod
    def filter_file(file: Path):
        return file.name.endswith(".wfp")

    def load_all(self) -> Dict[str, "TFModel"]:
        ret = {}
        for path in self.filter_files(list_dir(self.location)):
            name = path.name.split(".")[0]
            model = self.load(name)
            ret[model.name] = model
        return ret
