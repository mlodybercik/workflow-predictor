from typing import TYPE_CHECKING, Any, Dict, Set

import keras as K
import numpy as np

from . import logger
from .types import ModelABC

if TYPE_CHECKING:
    from learn.model_mapping import InvTransform

    from .loader import ModelLoader

logger = logger.getChild("model")


class TFModel(ModelABC):
    type = "tensorflow"
    name: str
    meta: Dict[str, Any]
    time_params: Dict[str, float]
    params: Set[str]
    model: "K.Model"
    inv_mapping: "InvTransform"

    def __init__(self, meta: Dict[str, Any], model: "K.Model", inv_mapping: "InvTransform"):
        self.meta = meta
        self.name = meta["name"]
        self.time_params = meta["mapping_params"]
        self.params = set(meta["inputs"])
        self.model = model
        self.inv_mapping = inv_mapping

    def predict(self, /, **kwargs) -> float:
        logger.debug(f"Predicting time for node {self.name}")
        # FIXME: this
        parameters = dict.fromkeys(self.params, "")  # create dictionary from all of the model parameters
        parameters.update(kwargs)  # join them, to make sure that all parameters that are required exist
        parameters = {k: np.array([v], dtype=np.float32) for k, v in parameters.items() if k in self.params}
        # we should use .predict due to:
        # https://keras.io/getting_started/faq/#whats-the-difference-between-model-methods-predict-and-call
        return self.inv_mapping(K.backend.get_value(self.model.predict(parameters)).flat[0], self.time_params)


class BlankModel(ModelABC):
    type = "blank"

    def __init__(self, name: str):
        self.name = name

    def predict(self, /, **kwargs) -> float:
        return 1.0


class ModelBank:
    loader: "ModelLoader"
    bank: Dict[str, "TFModel"]

    def __init__(self, loader: "ModelLoader"):
        self.bank = {}
        self.loader = loader

    def __getitem__(self, key: str) -> "TFModel":
        try:
            return self.bank[key]
        except KeyError:
            logger.error(f"Requested model {key} doesn't exist! Creating empty model object with 1s time", exc_info=0)
            self.bank[key] = BlankModel(key)

    def load(self, name: str) -> "TFModel":
        model = self.loader.load(name)
        self.bank[name] = model
        return model

    def load_all(self):
        self.bank.update(self.loader.load_all())
