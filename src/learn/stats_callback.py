from io import StringIO

from keras.callbacks import Callback, CSVLogger

from . import logger

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

    def on_epoch_begin(self, epoch, logs=None):
        logger.info(f"Starting epoch {epoch}")
        return super().on_epoch_begin(epoch, logs)

    def on_train_end(self, logs=None):
        self.csv_file.seek(0)
        self.writer = None
