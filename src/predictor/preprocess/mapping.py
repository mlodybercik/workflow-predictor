# flake8: noqa: F405
import typing as T

from .bulk import *  # noqa: F405

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

MAPPING: T.Dict[str, T.Callable[[str, T.Any], T.Dict[str, T.Union[int, str]]]] = {
    "api-version": drop,
    "approach": drop,
    "as-of-date": drop,
    "as-of-datetime": drop,
    "batch-instance-seq": batch_instance_seq,
    "batch-workflow": batch_workflow,
    "bsinp-run-id": bsinp_run_id,
    "business-date": drop,
    "business-day": business_day,
    "chf-usd-rate": drop,
    "correlation-id": drop,
    "failed-job-id": drop,
    "failed-job-status": drop,
    "failed-job-uid": drop,
    "flow-type": drop,
    "regulatory-authority": drop,
    "hac-run-id": hac_run_id,
    "ib-run-id": ib_run_id,
    "pb-run-id": pb_run_id,
    "process-flag": process_flag,
    "processing-location": processing_location,
    "rd-run-id": rd_run_id,
    "regulatory-approaches": regulatory_approaches,
    "rules-branch": rules_branch,
    "scenario-workflow": drop,
    "setenv": drop,
    "skip-ler": skip_ler,
    "skip-mdl-landing": skip_mdl_landing,
    "skip-mdl-out": skip_mdl_out,
    "source-type": source_type,
}


def generate_from_order(params: T.Sequence[T.Any]):
    length = len(params)
    return {param: (i / length) - 0.5 for i, param in enumerate(params)}
