# isort: skip_file
from predictor import init_logger

logger = init_logger("INFO")

from .learn import ModelLearn  # noqa: E402

__all__ = ["ModelLearn"]
