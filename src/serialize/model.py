import marshal
import types
from datetime import datetime
from io import BytesIO
from json import dumps, loads
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple
from zipfile import ZIP_DEFLATED, ZipFile

import numpy as np
import tensorflow as tf

from . import logger

if TYPE_CHECKING:
    from learn.time_preprocess_mapping import InvTransform

logger = logger.getChild("model")


class ModelSerializer:
    _buffer: Optional[BytesIO]
    _zip: Optional[ZipFile]
    model_path: Path
    name: str

    def __init__(self, model_path: str, mode: str):
        self.model_path = Path(model_path).absolute()
        if self.model_path.is_dir():
            raise ValueError(f"{model_path} is a directory")
        self.name = self.model_path.name.split(".")[0]
        self._buffer = None
        self._zip = None
        self.mode = mode

    def __enter__(self):
        self._buffer = BytesIO()
        if self.mode == "r":
            with open(self.model_path, "rb") as file:
                self._buffer.write(file.read())
        self._zip = ZipFile(self._buffer, self.mode, ZIP_DEFLATED)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._zip.close()
        if self.mode == "w":
            with open(self.model_path, "wb") as file:
                file.write(self._buffer.getbuffer())
        self._buffer.close()

        self._buffer = None
        self._zip = None

    def save_model_to_zip(
        self,
        model: tf.keras.Model,
        inverse_mapping: "InvTransform",
        mapping_params: Dict[str, float],
        stats: Optional[str] = None,
        *args,
        **params,
    ):
        if not self._zip:
            raise RuntimeError("class should be handled only with with keyword")
        if self.mode != "w":
            raise RuntimeError("tried to write to readonly file")

        model_declaration = model.get_config()
        model_weights = [i.tolist() for i in model.get_weights()]
        mapping_func = marshal.dumps(inverse_mapping.__code__)
        info = {
            "name": self.name,
            "create_time": datetime.now().isoformat(),
            "layers": len(model.layers),
            "inputs": [str(i.name) for i in model.inputs],
            "mapping_params": mapping_params,
        }
        self._zip.writestr("inverse_mapping.pyfunc", mapping_func)
        self._zip.writestr("declaration.json", dumps(model_declaration).encode())
        self._zip.writestr("weights.json", dumps(model_weights).encode())
        self._zip.writestr("meta/info.json", dumps(info).encode())

        if params:
            self._zip.writestr("meta/params.json", dumps(params).encode())
        if args:
            self._zip.writestr("meta/args.json", dumps(args).encode())
        if stats:
            self._zip.writestr("meta/stats.csv", stats.encode())

    def load_stats_from_zip(self):
        if not self._zip:
            raise RuntimeError("class should be handled only with with keyword")
        if self.mode == "w":
            raise RuntimeError("tried to read from writeonly file")

        for item in self._zip.filelist():
            if item.filename == "meta/stats.csv":
                return self._zip.read(item).decode()
        return None

    def load_model_from_zip(self) -> Tuple[tf.keras.Model, Dict[str, Any], "InvTransform"]:
        # serializing and deserializing in this way requires the whole model to
        # to be decompressed into memory, and then loaded as a model. this could
        # cause problems when handling huge models

        model_declaration = loads(self._zip.read("declaration.json").decode())
        model_weights = [np.array(layer) for layer in loads(self._zip.read("weights.json").decode())]

        info = loads(self._zip.read("meta/info.json").decode())
        raw_inv_func = marshal.loads(self._zip.read("inverse_mapping.pyfunc"))
        inv_func = types.FunctionType(raw_inv_func, globals(), "inverse_func")

        if info["name"] != self.name:
            logger.warning(f"Loaded filename doesn't match model name '{info['name']}' != '{self.name}'")

        model = tf.keras.Model.from_config(model_declaration)
        model.set_weights(model_weights)

        return model, info, inv_func
