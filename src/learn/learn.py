from pathlib import Path
from typing import Dict, List

import pandas as pd
import tensorflow as tf
from sklearn.model_selection import (
    train_test_split,  # TODO: to be honest we dont need it, we could implment own version
)
from yaml import CLoader, load

from learn.time_preprocess_mapping import TIME_MAPPING
from predictor.preprocess.mapping import MAPPING
from serialize.model import ModelSerializer

from . import logger
from .data_generator import DictDataGenerator
from .stats_callback import InMemoryCSVLogger
from .tf_model import create_model_from_params

logger = logger.getChild("learn")


class ModelLearn:
    maestro_calculated: Path
    task_columns: Dict[str, List[str]]
    data: pd.DataFrame
    dump_path: Path

    def __init__(self, maestro_calculated: str, task_columns: str, dump_path: str) -> None:
        self.maestro_calculated = Path(maestro_calculated).absolute()
        self.dump_path = Path(dump_path).absolute()
        task_columns_location = Path(task_columns).absolute()

        if not self.maestro_calculated.exists():
            raise ValueError(f"Maestro calculated path '{maestro_calculated}' doesn't exist")
        if self.maestro_calculated.is_dir():
            raise ValueError(f"Maestro calculated path '{maestro_calculated}' is a directory")

        if not task_columns_location.exists():
            raise ValueError(f"Task parameters definition '{task_columns}' doesn't exist")
        if task_columns_location.is_dir():
            raise ValueError(f"Task parameters definition '{task_columns}' is a directory")

        if not self.dump_path.exists():
            raise ValueError(f"Task parameters definition '{dump_path}' doesn't exist")
        if not self.dump_path.is_dir():
            raise ValueError(f"Task parameters definition '{dump_path}' is a file")

        with open(task_columns_location) as file:
            self.task_columns = load(file, CLoader)

        self.data = pd.read_csv(self.maestro_calculated, low_memory=False)

    def preprocess_times(self, job_name: str):
        current_job_times = self.data[self.data["job_name"] == job_name]["processing-time"]

        q05 = float(current_job_times.quantile(0.05))
        q95 = float(current_job_times.quantile(0.95))
        min = float(current_job_times.min())
        max = float(current_job_times.max())
        mean = float(current_job_times.mean())
        std = float(current_job_times.std())
        median = float(current_job_times.median())

        mapping_params = dict(q05=q05, q95=q95, min=min, max=max, mean=mean, std=std, median=median)
        logger.debug(mapping_params)

        func, inv_func = TIME_MAPPING[job_name]

        self.data.loc[self.data["job_name"] == job_name, "processing-time"] = func(current_job_times, mapping_params)
        return inv_func, mapping_params

    def learn(self, split_dataset=True, split_ratio=0.8, batch_size=8, epochs=20):
        for job in self.data["job_name"].unique():
            logger.info(f"Starting {job}")

            inv_func, mapping_params = self.preprocess_times(job)

            job_train = self.data[self.data["job_name"] == job]

            # for production, we should train model on all of the data
            if split_dataset:
                job_train, job_test = train_test_split(job_train, test_size=1 - split_ratio)

            # first we build the model, to do that we need list of required parameters
            parameters = {}
            for parameter in self.task_columns[job]:
                parameters.update(MAPPING[parameter](parameter, job_train.iloc[0][parameter]))

            # we get the model, and input/output signature
            # TODO: create models from some kind of override file
            model, signature, shape = create_model_from_params(parameters.keys())

            # we create the dataset
            DATASET = tf.data.Dataset.from_generator(
                DictDataGenerator(job_train, self.task_columns[job]),
                output_types=signature,
                output_shapes=shape,
            )

            # and do the usual
            model.compile(
                optimizer=tf.keras.optimizers.SGD(learning_rate=0.00005, momentum=True),
                loss="mse",
            )
            csv_logger = InMemoryCSVLogger()
            model.fit(DATASET, epochs=epochs, batch_size=batch_size, verbose=False, callbacks=[csv_logger])

            if split_dataset:
                DATASET_VAL = tf.data.Dataset.from_generator(
                    DictDataGenerator(job_test, self.task_columns[job]),
                    output_types=signature,
                    output_shapes=shape,
                )
                logger.info(f"{job}'s loss = {model.evaluate(DATASET_VAL, verbose=False)}")

            with ModelSerializer(f"/tmp/models/{job}.wfp", "w") as serializer:
                serializer.save_model_to_zip(model, inv_func, mapping_params, csv_logger.csv_file.getvalue())
