import typing as T

from numpy import nan

from worklogger import get_logger

logger = get_logger(__name__)

DEFAULT_BOOL = {"0": 0, "1": 1, 0: 0, 1: 1, "false": 0, "true": 1, "False": 0, "True": 1, False: 0, True: 1}

# fmt: off
EMPTY = {}
BATCH_WORKFLOW_MAPPING = {
    "STRATEGIC_PAC": 0, "STRATEGIC_EUR": 1, "STRATEGIC_AMS": 2, "STRATEGIC_SEC": 3, "STRATEGIC_CH": 4,
}
BUSINESS_DAY_MAPPING = {  # FIXME: should NaN be 4?
    nan: 4, "BD0": 0,  "BD1": 1, "BD2": 2, "BD3": 3, "BD4": 4, "BD5": 5, "BD6": 6, "BD7": 7, "BD8": 8, "BD9": 9,
}
PROCESS_FLAG_MAPPING = {"N": 1, nan: 0}
PROCESSING_LOCATION_LIST = set(['PAC', 'EUR', 'AMS', 'SEC', 'CH'])
REGULATORY_APPROACH_MAPPING = {"ONLY-B3": 0, "NON-B3": 1}
RULES_BRANCH_MAPPING = {"PROD_SA": 0, "UAT": 1, nan: -1}
SKIP_MDL_LANDING_MAPPING = {nan: -1, **DEFAULT_BOOL}
SKIP_MDL_OUT_MAPPING = {nan: 0, **DEFAULT_BOOL}
SOURCE_TYPE_LIST = set(["IB", "PB"])
SKIP_LER_MAPPING = {nan: -1, **DEFAULT_BOOL}
# fmt: on


def drop(_, __):
    return EMPTY


def pass_(name: str, value: T.Any):
    return {name: value}


class SimpleMapping:
    def __init__(self, name: str, mapping: T.Dict[str, int], default: T.Optional[int] = None) -> None:
        self.name = name
        self.mapping = mapping
        self.default = default

    def __getitem__(self, name: str):
        try:
            return self.mapping[name]
        except KeyError:
            logger.debug(f"Mapping in {self.name} missing for value: '{name}', is that an error?")
            if self.default is not None:
                return self.default
            raise KeyError(f"simple mapping failed for {self.name}")

    def __call__(self, name: str, value: str) -> T.Dict[str, int]:
        return {name: self[value]}


class SimpleChangeType:
    def __init__(self, name: str, type: T.Type[float], default: T.Optional[float] = None) -> None:
        self.name = name
        self.type = type
        self.default = default

    def __call__(self, name: str, value: str) -> T.Dict[str, int]:
        try:
            return {name: self.type(value)}
        except ValueError:
            if value == nan or self.default is not None:
                return {name: self.default}
            logger.debug(f"ChangeType in {self.name} raised ValueException for value: '{value}'")
            raise KeyError(f"simple change type failed for {self.name}")


batch_instance_seq = SimpleChangeType("batch-instance-seq", int, 0)
batch_workflow = SimpleMapping("batch-workflow", BATCH_WORKFLOW_MAPPING, -1)

# FIXME: idk, wether offset of >130 from zero will cause trouble
bsinp_run_id = SimpleChangeType("bsinp-run-id", int, -1)
business_day = SimpleMapping("business-day", BUSINESS_DAY_MAPPING, -1)

# FIXME: hac-run-id is (was?) highly correlated with business-day
hac_run_id = SimpleChangeType("hac-run-id", int, 0)

# FIXME: same as the above
ib_run_id = SimpleChangeType("ib-run-id", int, -1)

# FIXME: again, offset of 615 could fuck with the ML
pb_run_id = SimpleChangeType("pb-run-id", int, -1)

process_flag = SimpleMapping("process-flag", PROCESS_FLAG_MAPPING, 0)


def processing_location(name: str, value: str) -> T.Dict[str, int]:
    ret = dict.fromkeys(PROCESSING_LOCATION_LIST, 0)
    try:
        for item in value.split(","):
            ret[item] = 1
    except KeyError:
        raise KeyError(f"unknown processing-location {item}")
    return {f"{name}-is-{k.lower()}": v for k, v in ret.items()}


rd_run_id = SimpleChangeType("rd-run-id", int, 0)
regulatory_approaches = SimpleMapping("regulatory-approaches", REGULATORY_APPROACH_MAPPING, -1)
rules_branch = SimpleMapping("rules-branch", RULES_BRANCH_MAPPING, -1)
skip_ler = SimpleMapping("skip-ler", SKIP_LER_MAPPING, -1)
skip_mdl_landing = SimpleMapping("skip-mdl-landing", SKIP_MDL_LANDING_MAPPING, -1)
skip_mdl_out = SimpleMapping("skip-mdl-out", SKIP_MDL_OUT_MAPPING, 0)


# FIXME: does order make a difference?
def source_type(name: str, value: str) -> T.Dict[str, int]:
    ret = dict.fromkeys(SOURCE_TYPE_LIST, 0)
    try:
        for item in value.split(","):
            if item in ret:
                ret[item] = 1
    except KeyError:
        raise KeyError(f"unknown processing-location '{item}'")
    except AttributeError:
        pass
    return {f"{name}-is-{k.lower()}": v for k, v in ret.items()}
