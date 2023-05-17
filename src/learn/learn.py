from pathlib import Path
from typing import Dict, List

import pandas as pd
import tensorflow as tf
from sklearn.model_selection import (
    train_test_split,  # TODO: to be honest we dont need it, we could implment own version
)
from yaml import CLoader, load

from predictor.preprocess.mapping import MAPPING

from . import logger
from .data_generator import DictDataGenerator
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
        self.preprocess_time()

    def preprocess_time(self):
        for job in self.data["job_name"].unique():
            current_job_times = self.data[self.data["job_name"] == job]["processing-time"]

            mean = current_job_times.mean()
            std = current_job_times.std()
            median = current_job_times.median()

            if mean > 0:
                self.data.loc[self.data["job_name"] == job, "processing-time"] = (current_job_times - median) / std
            else:
                self.data.loc[self.data["job_name"] == job, "processing-time"] = current_job_times - median

    def learn(self, split_dataset=True, split_ratio=0.8, batch_size=2):
        jobs = self.data["job_name"].unique()

        for job in jobs:
            print(f"Starging {job}")
            job_train = self.data[self.data["job_name"] == job]
            # for production, we should train model on all of the
            if split_dataset:
                job_train, job_test = train_test_split(job_train, test_size=1 - split_ratio)

            # first we build the model, to do that we need list of required parameters
            parameters = {}
            for parameter in self.task_columns[job]:
                parameters.update(MAPPING[parameter](parameter, job_train.iloc[0][parameter]))

            model = create_model_from_params(parameters.keys())

            # we specify the output types for tf to use
            output_type = {k: (tf.float32) for k in parameters.keys()}, tf.float32

            # we create the dataset
            DATASET = tf.data.Dataset.from_generator(
                DictDataGenerator(job_train, self.task_columns[job], 1), output_types=output_type
            )

            # and do the usual
            model.compile(
                optimizer=tf.keras.optimizers.SGD(learning_rate=0.0001, momentum=True),
                loss="mse",
            )

            model.fit(DATASET, epochs=10, batch_size=batch_size)

            if split_dataset:
                DATASET_VAL = tf.data.Dataset.from_generator(
                    DictDataGenerator(job_test, self.task_columns[job], 1), output_types=output_type
                )
                print(f"{job}'s loss = {model.evaluate(DATASET_VAL)}")
