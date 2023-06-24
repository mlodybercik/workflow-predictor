# flake8: noqa: F405
import typing as T

USABLE_PARAMETERS = {
    "batch-instance-seq",
    "batch-workflow",
    "bsinp-run-id",
    "business-day",
    "hac-run-id",
    "ib-run-id",
    "pb-run-id",
    "process-flag",
    "processing-location",
    "rd-run-id",
    "regulatory-approaches",
    "rules-branch",
    "skip-ler",
    "skip-mdl-landing",
    "skip-mdl-out",
    "source-type",
}


def generate_from_order(params: T.Sequence[T.Any]):
    length = len(params)
    return {param: (i / length) - 0.5 for i, param in enumerate(params)}
