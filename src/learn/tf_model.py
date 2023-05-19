from typing import TYPE_CHECKING, List, Tuple

import keras.layers as layers
import keras.models as models
import tensorflow as tf

if TYPE_CHECKING:
    from .model_mapping import ModelDefType


def create_model_from_params(parameters: List[str], raw_model: "ModelDefType") -> Tuple[models.Model, tuple, tuple]:
    # parameters should be a list of keys in a dict *after* preprocessing,
    # as preprocessing sometimes adds few more columns

    if len(raw_model[0]) + 1 != len(raw_model[1]):
        raise AttributeError("model definition is bad, model should have one additional attribute for output layer")

    inputs = {}

    for parameter in parameters:
        inputs[parameter] = layers.Input(shape=(1,), dtype=tf.float32, name=parameter)

    # those two layers cant be edited directly
    all_values = layers.Concatenate(axis=-1)(list(inputs.values()))
    previous = layers.Flatten()(all_values)

    for layer, params in zip(*raw_model):
        previous = layer(**params)(previous)

    raw_model[1][-1].pop("units", None)

    output = layers.Dense(1, **raw_model[1][-1])(previous)

    output_signature = {k: (tf.float32) for k in parameters}, tf.float32
    output_shape = {k: (1,) for k in parameters}, (1,)

    return models.Model(inputs=inputs, outputs=output), output_signature, output_shape


def undershoot_penalize(y_true, y_pred):
    error = y_true - y_pred
    condition = tf.less(error, 0)
    over_loss = tf.abs(error)
    unde_loss = tf.square(error)
    return tf.reduce_mean(tf.where(condition, over_loss, unde_loss), -1)
