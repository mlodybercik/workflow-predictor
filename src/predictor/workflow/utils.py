import os
from pathlib import Path
from typing import List


def list_dir(path: Path) -> List[Path]:
    if not path.is_dir():
        raise TypeError("provided path is not a directory")
    return [(path / Path(item)).absolute() for item in os.listdir(path)]
