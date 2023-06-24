import typing as T

import numpy as np
import pandas as pd

from predictor.preprocess.mapping import generate_from_order


class DictDataGenerator:
    def __iter__(self):
        row_iterator = self.data.iterrows()
        while True:  # is this safe?
            X = dict.fromkeys(self.raw_parameters)
            try:
                _, row = next(row_iterator)
            except StopIteration:
                return
            for parameter in X:
                X[parameter] = self.parameters[parameter][row[parameter]]
            yield {k: np.array([v], dtype=np.float32) for k, v in X.items()}, np.array(
                [float(row["processing-time"])], dtype=np.float32
            )

    def __call__(self):
        return self.__iter__()

    def __init__(self, data: pd.DataFrame, parameters: T.Dict[str, T.List[T.Any]]):
        self.data = data
        self.parameters = {k: generate_from_order(v) for k, v in parameters.items()}
        self.raw_parameters = parameters.keys()
