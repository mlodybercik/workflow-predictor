from typing import TYPE_CHECKING, Dict

from . import logger
from .types import Model, ModelType

if TYPE_CHECKING:
    from .loader import ModelLoader

logger = logger.getChild("model")


class BlankModel(Model):
    model_type = ModelType.BLANK

    def __init__(self, name: str, time: float):
        self.time = time
        super().__init__(name)

    def predict(self, /, **kwargs) -> float:
        return self.time


class ModelBank:
    loader: "ModelLoader"
    bank: Dict[str, "Model"]

    def __init__(self, loader: "ModelLoader"):
        self.bank = {}
        self.loader = loader

    def __getitem__(self, key: str) -> "Model":
        try:
            return self.bank[key]
        except KeyError:
            logger.exception(f"Model missing for key '{key}'")
            # FIXME: remove this return default missing model
            # TODO: we could change this default into some kind of a lazyloader
            return BlankModel(1)

    def load(self, name: str) -> "Model":
        logger.debug(f"FIXME: Attempting to load '{name}'")
        model = self.loader.load(name)
        self.bank[name] = model
        return model

    def load_all(self):
        logger.info("Attempting to load all")
        self.bank.update(self.loader.load_all())
