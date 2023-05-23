from io import StringIO
from typing import TYPE_CHECKING

import numpy as np
from keras.callbacks import Callback, CSVLogger

from . import logger

if TYPE_CHECKING:
    import tensorflow as tf

    from .model_mapping import InvTransform

logger = logger.getChild("callbacks")


class InMemoryCSVLogger(CSVLogger):
    buffer: StringIO

    def __init__(self, separator=",", append=False):
        self.sep = separator
        self.append = append
        self.writer = None
        self.keys = None
        self.append_header = True
        super(Callback, self).__init__()

    def on_train_begin(self, logs=None):
        if self.append:
            raise ValueError("append not supported")
        self.csv_file = StringIO()

    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        out = [f"{name} = {logs[name]:.4f}" for name in logs.keys()]
        logger.info(f"Epoch {epoch} finished, {', '.join(out)}")
        super().on_epoch_end(epoch, logs)

    def on_train_end(self, logs=None):
        self.csv_file.seek(0)
        self.writer = None


class RealPerformanceCallback(Callback):
    inv_transform: "InvTransform"
    inv_mapping: dict

    dataset: "tf.data.Dataset"

    def __init__(self, test_dataset: "tf.data.Dataset", inv_transform: "InvTransform", inv_mapping: dict):
        self.test_dataset = test_dataset
        self.inv_transform = inv_transform
        self.inv_mapping = inv_mapping
        super().__init__()

    def on_epoch_end(self, epoch, logs=None):
        if logs:
            scores = self.inv_transform(
                self.model.predict(self.test_dataset, verbose=0, batch_size=1).flatten(), self.inv_mapping
            )
            mean, std, min, max = np.mean(scores), np.std(scores), np.min(scores), np.max(scores)

            logs["inv_loss"] = mean
            logs["inv_std"] = std
            logs["inv_min"] = min
            logs["inv_max"] = max
        else:
            logger.debug("Logs missing?")
