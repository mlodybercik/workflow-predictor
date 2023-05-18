from abc import ABC, abstractmethod, abstractstaticmethod
from pathlib import Path
from typing import Dict, List


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
    def load_all(self) -> Dict[str, "ModelABC"]:
        ...

    @abstractmethod
    def load(self, name: str):
        ...


class ModelABC(ABC):
    type: str

    @abstractmethod
    def predict(self, /, **kwargs) -> float:
        ...
