from collections import UserDict
from functools import lru_cache
from typing import TYPE_CHECKING, Any, Dict

import keras as K
import numpy as np

from worklogger import get_logger

from .types import ModelABC

if TYPE_CHECKING:
    from learn.model_mapping import InvTransform

    from .loader import ModelLoader

logger = get_logger(__name__)


class TFModel(ModelABC):
    type = "tensorflow"
    name: str
    meta: Dict[str, Any]
    time_params: Dict[str, float]
    model: "K.Model"
    inv_mapping: "InvTransform"

    def __init__(
        self,
        meta: Dict[str, Any],
        model: "K.Model",
        parameters: Dict[str, Dict[Any, float]],
        inv_mapping: "InvTransform",
    ):
        self.meta = meta
        self.name = meta["name"]
        self.mapping_parameters = parameters
        self.time_params = meta["mapping_params"]
        self.model = model
        self.inv_mapping = inv_mapping

    @lru_cache
    def predict(self, /, **kwargs) -> float:
        logger.debug(f"Predicting time for node {self.name}")

        # create dictionary from all of the model parameters
        parameters = dict.fromkeys(self.mapping_parameters, "")

        # join them, to make sure that all parameters that are required exist
        parameters.update({k: v for k, v in kwargs.items() if k in self.mapping_parameters})

        for parameter, value in parameters.items():
            try:
                parameters[parameter] = self.mapping_parameters[parameter][value]
            except KeyError:
                logger.warning(f"Node '{self.name}' has never seen '{value}' in '{parameter}', returning 0")
                parameters[parameter] = 0

        parameters = {k: np.array([v], dtype=np.float32) for k, v in parameters.items()}
        time = self.inv_mapping(K.backend.get_value(self.model(parameters)).flat[0], self.time_params)
        if time < 0:
            return 0
        return time


class BlankModel(ModelABC):
    mapping_parameters = dict()
    type = "blank"

    def __init__(self, name: str):
        self.name = name

    def predict(self, /, **kwargs) -> float:
        return 1.0


class ModelBank(UserDict[str, "ModelABC"]):
    loader: "ModelLoader"

    def __init__(self, loader: "ModelLoader"):
        super().__init__()
        self.loader = loader

    def __getitem__(self, key: str) -> "ModelABC":
        try:
            return self.data[key]
        except KeyError:
            logger.error(f"Requested model {key} doesn't exist! Creating empty model object with 1s time", exc_info=0)
            self.data[key] = (model := BlankModel(key))
            return model

    def load(self, name: str) -> "TFModel":
        model = self.loader.load(name)
        self[name] = (model := self.loader.load(name))
        return model

    def load_all(self):
        self.update(self.loader.load_all())
