import csv
from collections import defaultdict
import yaml
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
    'hac-run-id', 'business-day', 'processing-location-is-ams', 'processing-location-is-ch', 
    'processing-location-is-eur', 'processing-location-is-pac', 'processing-location-is-sec',
    'source-type-is-ib', 'source-type-is-pb',
}

columns_per_task = defaultdict(set)

# which rows to delete?
failed = lambda row: not bool(row['failed-job-id'])
to_remove = [failed]

# which columns to remove?
columns_to_remove = {'params', 'processing-location', 'failed-job-id', 'failed-job-uid', 'source-type'}

with open('data/maestro-history-clean.csv', 'w') as file_w:
    with open('data/maestro-history.csv') as file_r:
        reader = csv.DictReader(file_r, lineterminator='\n')
        header = set([*next(reader), *all_commands])
        header.difference_update(columns_to_remove)

        writer = csv.DictWriter(file_w, header, lineterminator='\n')
        writer.writeheader()

        for line in reader:
            params = line.pop('params')
            iterator = iter(shlex.split(params))
            parsed_params = dict.fromkeys(all_commands, '')

            # group params in pairs to extract them into columns
            for item in iterator:
                parameter = item.removeprefix("--")
                parsed_params[parameter] = next(iterator)

                # get list of parameters used for any task
                columns_per_task[line["job_name"]].add(parameter)

            if (loc := parsed_params['processing-location']):
                for name in loc.split(","):
                    parsed_params[f'processing-location-is-{name.lower()}'] = 1

            if (source_type := parsed_params['source-type']):
                for name in source_type.split(","):
                    parsed_params[f'source-type-is-{name.lower()}'] = 1


            new_row = {**line, **parsed_params}

            # if any of the to_remove macros return true, skip that line
            if any([i(new_row) for i in to_remove]):
                writer.writerow({k: v for k, v in new_row.items() if k in header})

with open("data/task-columns.yml", "w") as file:
    file.write(yaml.dump({key: list(columns) for key, columns in columns_per_task.items()}, Dumper=yaml.CDumper))
