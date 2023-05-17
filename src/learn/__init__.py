# isort: skip_file
import logging

logger = logging.getLogger(__name__).getChild("learn")

from .learn import ModelLearn  # noqa: E402

__all__ = ["ModelLearn"]
