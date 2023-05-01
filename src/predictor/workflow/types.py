from abc import ABC, abstractmethod, abstractstaticmethod
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List


class ModelType(Enum):
    BLANK = auto()
    LINEAR = auto()
    NEURAL = auto()


class Loader(ABC):
    location: Path

    def __init__(self, location: Path):
        if not location.exists():
            raise ValueError(f"Loader path doesn't exist, {location.absolute()}")
        if not location.is_dir():
            raise ValueError(f"Loader path is not a directory, {location.absolute()}")
        self.location = location.absolute()

    @classmethod
    def filter_files(cls, paths: List[Path]) -> List[Path]:
        return [i for i in paths if cls.filter_file(i)]

    @abstractstaticmethod
    def filter_file(path: Path) -> bool:
        ...

    @abstractmethod
    def load_all(self) -> Dict[str, "Model"]:
        ...

    @abstractmethod
    def load(self, name: str):
        ...


class Model(ABC):
    model_type: ModelType
    name: str

    def __init__(self, name: str):
        self.name = name

    # @abstractmethod
    def predict(self, /, **kwargs) -> float:
        pass