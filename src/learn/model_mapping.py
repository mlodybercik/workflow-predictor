from collections import defaultdict
from typing import TYPE_CHECKING, Any, Callable, Dict, Sequence, Tuple

import keras.layers as layers
import keras.losses as losses
import keras.optimizers as optimizers

if TYPE_CHECKING:
    import pandas as pd

# Types
TransformFunc = Callable[["pd.DataFrame", Dict[str, float]], "pd.DataFrame"]
InvTransform = Callable[[float, Dict[str, float]], float]

ModelDefType = Tuple[Sequence[layers.Layer], Sequence[Dict[str, Any]]]
CompileDefType = Dict[str, Any]


# defaults
def DEFAULT(job_times: "pd.DataFrame", params: "Dict[str, float]") -> "pd.DataFrame":
    # for mapping original into learning space we dont need params dict cos we could
    # calculate them from job_times variable, but to keep the same convetion
    # with usage of INV_DEFAULT we'll pass them from outside ¯\_(ツ)_/¯
    if params["mean"] > 1:
        return (job_times - params["mean"]) / params["mean"]
    return job_times / params["max"]


def INV_DEFAULT(predicted: float, params: "Dict[str, float]") -> float:
    if params["mean"] > 1:
        return (predicted * params["mean"]) + params["mean"]
    return predicted * params["max"]


default_model: ModelDefType = (
    (layers.Dense, layers.Dense, layers.Dense),
    (
        {"units": 60, "activation": "relu"},
        {"units": 20, "activation": "relu"},
        {"units": 10, "activation": "relu"},
        {},
    ),
)

short_model: ModelDefType = ((layers.Dense, layers.Dense), ({"units": 10}, {"units": 10, "activation": "relu"}, {}))

default_compile: CompileDefType = {
    "optimizer": (optimizers.Adam, {"learning_rate": 0.0001}),
    "loss": losses.MeanSquaredError(),
}

# put neccessary functions here

TIME_MAPPING: Dict[str, Tuple[TransformFunc, InvTransform]] = defaultdict(
    lambda: (DEFAULT, INV_DEFAULT),
    {
        # put time mapping functions overrides here, you have to implement those functions
        # "ultra-mega-rare-job-3000": (map_to_time_dim, map_to_real_dim))
    },
)


MODEL_MAPPING: Dict[str, ModelDefType] = defaultdict(
    lambda: default_model,
    {
        "b3-calc-completed": short_model,
        "complete-strategic-harmonization-job": short_model,
        "start-strategic-batch": short_model,
        "init-strategic-batch": short_model,
        "open-date-card": short_model,
        "f1-notification-trigger": short_model,
        # put model shape overrides here
        # "ultra-mega-rare-job-3000": (
        #       (layers.Dense, layers.Conv1D, layers.Sandwich),
        #       ({"units": 30}, {"filters": 5, "kernel_size": 2}, {"cheese": True}, {})
        # )
    },
)


COMPILE_MAPPING: Dict[str, CompileDefType] = defaultdict(
    lambda: default_compile.copy(),
    {
        # put compile overrides here
        # "ultra-mega-rare-job-3000": {
        #       "optimizer": (optimizers.Adam, {"learn_rate": 1e9}),
        #       "loss": best_mse_youve_ever_seen
        # }
    },
)
