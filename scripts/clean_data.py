import csv
import shlex

# params looks like this:
# --as-of-date 2022-07-29 --as-of-datetime 2022-07-30_03.08.13
# --batch-workflow STRATEGIC_PAC --business-date 2022-07-29
# --business-day BD0 --flow-type STRATEGIC
# --processing-location PAC
# 
# https://docs.python.org/3/library/shlex.html#shlex.split

all_commands = {
    'processing-location', 'bsinp-run-id', 'api-version', 'correlation-id', 'flow-type',
    'batch-workflow', 'rd-run-id', 'batch-instance-seq', 'chf-usd-rate', 'skip-mdl-out',
    'pb-run-id', 'setenv', 'regulatory-approaches', 'business-date', 'skip-mdl-landing',
    'ib-run-id', 'as-of-date', 'failed-job-status', 'as-of-datetime', 'failed-job-uid',
    'source-type', 'rules-branch', 'failed-job-id', 'scenario-workflow', 'process-flag',
    'hac-run-id', 'business-day'
}

# which rows to delete?
failed = lambda row: not bool(row["failed-job-id"])
to_remove = [failed]

# which columns to remove?
columns_to_remove = {
    "kafka_offset", "api-version", "skip-mdl-landing", "rd-run-id", "pb-run-id",
    "failed-job-id", "failed-job-uid", "chf-usd-rate", "setenv", "process-flag",
    "correlation-id", "failed-job-status", "scenario-workflow", "bsinp-run-id",
    "source-type", "params"
}

with open("data/maestro-history-clean.csv", "w") as file_w:
    with open("data/maestro-history.csv") as file_r:
        reader = csv.DictReader(file_r)
        header = set([*next(reader), *all_commands])
        header.difference_update(columns_to_remove)

        writer = csv.DictWriter(file_w, header)
        writer.writeheader()

        for line in reader:
            params = line.pop("params")
            iterator = iter(shlex.split(params))
            parsed_params = dict.fromkeys(all_commands, "")

            # group params in pairs to extract them into columns
            for item in iterator:
                parsed_params[item[2:]] = next(iterator)

            new_row = {**line, **parsed_params}

            # if any of the to_remove macros return true, skip that line
            if any([i(new_row) for i in to_remove]):
                writer.writerow({k: v for k, v in new_row.items() if k in header})
