from typing import List

import numpy as np
import pandas as pd

from predictor.preprocess.mapping import MAPPING


class DictDataGenerator:
    def __iter__(self):
        finished = False
        row_iterator = self.data.iterrows()
        while not finished:
            X = dict()
            try:
                _, row = next(row_iterator)
            except StopIteration:
                return
            for parameter in self.raw_parameters:
                for new_parameter, value in MAPPING[parameter](parameter, row[parameter]).items():
                    X[new_parameter] = value
            yield {k: np.array([v], dtype=np.float32) for k, v in X.items()}, np.array(
                [float(row["processing-time"])], dtype=np.float32
            )

    def __call__(self):
        return self.__iter__()

    def __init__(self, data: pd.DataFrame, raw_parameters: List[str]):
        self.data = data
        self.raw_parameters = raw_parameters
