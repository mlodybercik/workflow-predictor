import csv
from datetime import datetime

STATES = {"PROCESSING", "SUCCESS", "SUBMITTED"}

# im gonna create four columns:
# time from submitted to processing in cmd_time -> cmd_processing_time
# time from submitted to successs   in cmd_time -> cmd_success_time
# and 
# time from submitted to processing in event_time -> event_processing_time
# time from submitted to successs   in event_time -> event_success_time

def get_time(text: str):
    # time looks like this: 2022-07-30 05:08:24.0
    #                         %Y-%m-%d %H:%M:%S
    return datetime.strptime(text.removesuffix(".0"), "%Y-%m-%d %H:%M:%S")

grouper = dict()
done = dict()

with open("data/maestro-calculated.csv", "w") as file_w:
    with open("data/maestro-history-clean.csv") as file_r:
        reader = csv.DictReader(file_r, lineterminator="\n")
        headers = {
            "cmd_processing_time", "cmd_success_time",
            "event_processing_time", "event_success_time",
            *reader.fieldnames
        }
        [headers.remove(i) for i in ["status", "event_time", "cmd_time"]]
        writer = csv.DictWriter(file_w, headers, lineterminator="\n")
        writer.writeheader()

        for row in reader:
            if row["status"] in STATES:
                if row["uid"] not in grouper:
                    grouper[row["uid"]] = dict.fromkeys(STATES, None)
                grouper[row["uid"]][row["status"]] = row

                if not any([i == None for i in grouper[row["uid"]].values()]):
                    event_time_success = get_time(grouper[row["uid"]]["SUCCESS"]["event_time"])
                    event_time_submitted = get_time(grouper[row["uid"]]["SUBMITTED"]["event_time"])
                    event_time_processing = get_time(grouper[row["uid"]]["PROCESSING"]["event_time"])

                    cmd_time_success = get_time(grouper[row["uid"]]["SUCCESS"]["cmd_time"])
                    cmd_time_submitted = get_time(grouper[row["uid"]]["SUBMITTED"]["cmd_time"])
                    cmd_time_processing = get_time(grouper[row["uid"]]["PROCESSING"]["cmd_time"])

                    cmd_processing_time = int((cmd_time_processing - cmd_time_submitted).total_seconds())
                    cmd_success_time = int((cmd_time_success - cmd_time_submitted).total_seconds())
                    event_processing_time = int((event_time_processing - event_time_submitted).total_seconds())
                    event_success_time = int((event_time_success - event_time_submitted).total_seconds())

                    new_row = {
                        "cmd_processing_time": cmd_processing_time,
                        "cmd_success_time": cmd_success_time,
                        "event_processing_time": event_processing_time,
                        "event_success_time": event_success_time,
                        **row, 
                    }
                    writer.writerow({k: v for k, v in new_row.items() if k in headers})
                    del grouper[row["uid"]]

                

