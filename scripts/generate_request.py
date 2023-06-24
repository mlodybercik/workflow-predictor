import argparse
import csv
import json
import sys
from datetime import datetime
from get_times import get_time

headers_to_drop = [
    "api-version", "approach", "as-of-date", "as-of-datetime", "business-date", "chf-usd-rate",
    "correlation-id", "failed-job-id", "failed-job-status", "uid", "parent_uid"
    "failed-job-uid", "flow-type", "regulatory-authority", "scenario-workflow", "setenv", "business_date",
    "total-time", "kafka_offset", "waiting-time", "parent_uid", "workflow_name",
]

ret = {
    "processing": {},
    "done": {},
    "parameters": {}
}

path = ["reload-b3-audit", "reload-b3-tables", "b3-calc-completed", "run-b3-calculation", "complete-strategic-harmonization-job", "run-data-harmonization", "run-data-staging", "land-f1mdl-data", "start-strategic-batch", "init-strategic-batch", "open-date-card", "f1-notification-trigger"]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="generate template request to API")
    parser.add_argument("--job", "-j")
    parser.add_argument("--filename", "-f")
    args = parser.parse_args()

    job_dict = {}
    order = []

    with open(args.filename, "r") as file:
        reader = csv.DictReader(file, delimiter=";")
        headers = reader.fieldnames

        for row in reader:
            for header in headers_to_drop:
                row.pop(header, "")
            job_dict[row["job_name"]] = row
            order.append(row["job_name"])

    if args.job not in job_dict:
        print(f"Job '{args.job}' not in file {args.filename}")
        exit(1)

    for row in job_dict.values():
        for param, value in row.items():
            ret["parameters"][param] = value

    start_time = get_time(job_dict[order[0]]["cmd_time"])
    delta_time = datetime.now() - start_time

    i = 0

    while (current_job := order[i]) != args.job:
        job_time = get_time(job_dict[current_job]["cmd_time"]) + delta_time
        ret["done"][current_job] = int(job_time.timestamp())
        i += 1

    ret["parameters"].pop("processing-time", 0)
    print(json.dumps(ret))

    s = 0
    try:
        for item in path:
            s += float(job_dict[item]["processing-time"])
        print(s, file=sys.stderr)
    except KeyError as e:
        print(e, file=sys.stderr)
        pass