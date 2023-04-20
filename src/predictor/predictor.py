from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict

from .workflow.loader import ModelLoader, WorkflowLoader
from .workflow.model import ModelBank
from .workflow.workflow import Workflow


class Predictor:
    model_loader: ModelLoader
    model_bank: ModelBank
    workflows: Dict[str, Workflow] = {}
    workflow_loader: WorkflowLoader

    def __init__(self, model_directory: str, workflow_directory: str):
        model_path = Path(model_directory).absolute()
        workflow_path = Path(workflow_directory).absolute()

        if not model_path.exists():
            raise ValueError(f"Model path '{model_path}' doesn't exist")
        if not model_path.is_dir():
            raise ValueError(f"Workflow path '{model_path}' is not a directory")

        if not workflow_path.exists():
            raise ValueError(f"Model path '{workflow_path}' doesn't exist")
        if not workflow_path.is_dir():
            raise ValueError(f"Workflow path '{workflow_path}' is not a directory")

        self.model_loader = ModelLoader(model_path)
        self.model_bank = ModelBank(self.model_loader)

        self.model_bank.load_all()

        self.workflow_loader = WorkflowLoader(workflow_path, self.model_bank)

        self.workflows.update(self.workflow_loader.load_all())

    def test(self):
        print(
            self.workflows["securitization-flow"].predict(
                "reload-tactical-tables-post-securitization",
                {"complete-strategic-batch": datetime.now() - timedelta(seconds=30)},
                {"skip-regional-batches": datetime.now() - timedelta(seconds=21.37)},
            )
        )
