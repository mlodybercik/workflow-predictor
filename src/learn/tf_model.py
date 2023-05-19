from typing import List, Tuple

import keras.layers as layers
import keras.models as models
import tensorflow as tf


def create_model_from_params(parameters: List[str]) -> Tuple[models.Model, tuple, tuple]:
    # parameters should be a list of keys in a dict *after* preprocessing,
    # as preprocessing sometimes adds few more columns
    inputs = {}

    for parameter in parameters:
        inputs[parameter] = layers.Input(shape=(1,), dtype=tf.float32, name=parameter)

    all_values = layers.Concatenate(axis=-1)(list(inputs.values()))
    flatten = layers.Flatten()(all_values)

    l1 = layers.Dense(60, name="l1", activation="relu")(flatten)
    l2 = layers.Dense(30, name="l2", activation="relu")(l1)
    l3 = layers.Dense(10, name="l3", activation="relu")(l2)
    output = layers.Dense(1, name="output", activation="tanh")(l3)

    output_signature = {k: (tf.float32) for k in parameters}, tf.float32
    output_shape = {k: (1,) for k in parameters}, (1,)

    return models.Model(inputs=inputs, outputs=output), output_signature, output_shape
