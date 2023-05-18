from collections import defaultdict
from typing import TYPE_CHECKING, Callable, Dict, Tuple

if TYPE_CHECKING:
    import pandas as pd

TransformFunc = Callable[["pd.DataFrame", Dict[str, float]], "pd.DataFrame"]
InvTransform = Callable[[float, Dict[str, float]], float]


def DEFAULT(job_times: "pd.DataFrame", params: "Dict[str, float]") -> "pd.DataFrame":
    # for mapping original into learning space we dont need params dict cos we could
    # calculate them from job_times variable, but to keep the same convetion
    # with usage of INV_DEFAULT we'll pass them from outside ¯\_(ツ)_/¯
    if params["mean"] > 1:
        return (job_times - params["median"]) / params["mean"]
    return (job_times - params["min"]) / params["max"]


def INV_DEFAULT(predicted: float, params: "Dict[str, float]") -> float:
    if params["mean"] > 1:
        return (predicted * params["mean"]) + params["median"]
    return (predicted * params["max"]) + params["min"]


TIME_MAPPING: Dict[str, Tuple[TransformFunc, InvTransform]] = defaultdict(
    lambda: (DEFAULT, INV_DEFAULT),
    {
        # put time mapping functions overrides here
    },
)
