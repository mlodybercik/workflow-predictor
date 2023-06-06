import csv
from collections import defaultdict
from itertools import chain
import yaml
import shlex

# params looks like this:
# --as-of-date 2022-07-29 --as-of-datetime 2022-07-30_03.08.13
# --batch-workflow STRATEGIC_PAC --business-date 2022-07-29
# --business-day BD0 --flow-type STRATEGIC
# --processing-location PAC
# 
# https://docs.python.org/3/library/shlex.html#shlex.split


if __name__ == "__main__":
    columns_per_task = defaultdict(set)

    # which rows to delete?
    failed = lambda row: not bool(row['failed-job-id'])
    to_remove = [failed]

    # which columns to remove?
    columns_to_remove = {'params', 'failed-job-id', 'failed-job-uid'}
    all_commands = set()

    # TODO: use multithreading
    with open('data/maestro-history-clean.csv', 'w') as file_w:
        # open both files
        file_1 = open('data/maestro-history.csv', 'r')
        file_2 = open('data/maestro-history-v2.csv', 'r')

        # get sum of lengths
        length = sum(1 for _ in chain(file_1, file_2)) - 2  # - headers

        # get back to front
        file_1.seek(0)
        file_2.seek(0)

        # we dont need second header from the second file
        # we assume that all the columns are in the same order
        next(file_2)

        reader = csv.DictReader(chain(file_1, file_2), lineterminator='\n')
        # we need to get all the new columns from files
        for i, line in enumerate(reader):
            if not (i % 1000):
                print(f"[1/2]{i: 6d}/{length: 6d}", end="\r")

            params = line.pop('params')
            iterator = iter(shlex.split(params))
            for item in iterator:
                next(iterator)
                parameter = item.removeprefix("--")
                all_commands.add(parameter)

                # as we do it twice anyways, we could do it here...
                # get list of parameters used for any task
                columns_per_task[line["job_name"]].add(parameter)

        file_1.seek(0)
        file_2.seek(0)

        next(file_2)

        # just to be sure we recreate the new reader
        reader = csv.DictReader(chain(file_1, file_2), lineterminator='\n')

        header = set([*next(reader), *all_commands])
        header.difference_update(columns_to_remove)

        writer = csv.DictWriter(file_w, header, lineterminator='\n')
        writer.writeheader()

        for i, line in enumerate(reader):
            if not (i % 1000):
                print(f"[2/2]{i: 6d}/{length: 6d}", end="\r")

            params = line.pop('params')
            iterator = iter(shlex.split(params))
            parsed_params = dict.fromkeys(all_commands, '')

            # group params in pairs to extract them into columns
            for item in iterator:
                parameter = item.removeprefix("--")
                parsed_params[parameter] = next(iterator)

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


        file_1.close()
        file_2.close()

    with open("data/task-columns.yml", "w") as file:
        sorted_columns = sorted(columns_per_task.items(), key=lambda a: a[0])
        file.write(yaml.dump({key: sorted(row) for key, row in sorted_columns}, Dumper=yaml.CDumper))