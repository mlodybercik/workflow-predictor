import csv
from datetime import datetime

STATES = {"PROCESSING", "SUCCESS", "SUBMITTED"}

# im gonna create three columns:
# time from submitted to processing in event_time -> event-waiting-time
# time from processing to successs  in event_time -> event-processing-time
# time from submitted to successs   in event_time -> event-total-time

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
            "event-waiting-time", "event-processing-time",
            "event-total-time", *reader.fieldnames
        }

        [headers.remove(i) for i in ["status", "cmd_time"]]
        writer = csv.DictWriter(file_w, headers, lineterminator="\n")
        writer.writeheader()

        for row in reader:
            if row["status"] in STATES:
                if row["uid"] not in grouper:
                    grouper[row["uid"]] = dict.fromkeys(STATES, None)
                grouper[row["uid"]][row["status"]] = row

                if not any([i == None for i in grouper[row["uid"]].values()]):
                    time_success = get_time(grouper[row["uid"]]["SUCCESS"]["event_time"])
                    time_submitted = get_time(grouper[row["uid"]]["SUBMITTED"]["event_time"])
                    time_processing = get_time(grouper[row["uid"]]["PROCESSING"]["event_time"])

                    event_waiting_time = int((time_processing - time_submitted).total_seconds())
                    event_processing_time = int((time_success - time_processing).total_seconds())

                    # to to samo xD
                    # event_total_time = event_waiting_time + event_processing_time
                    event_total_time = int((time_success - time_submitted).total_seconds())

                    new_row = {
                        "event-waiting-time": event_waiting_time,
                        "event-processing-time": event_processing_time,
                        "event-total-time": event_total_time,
                        **row
                    }

                    writer.writerow({k: v for k, v in new_row.items() if k in headers})
                    del grouper[row["uid"]]

                

