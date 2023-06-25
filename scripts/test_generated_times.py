import requests
import argparse
import time
from generate_request import generate_dict_and_order, generate_params, ret


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="generate template request to API")
    parser.add_argument("--filename", "-f")
    parser.add_argument("--server", "-s", default="localhost:5000")
    args = parser.parse_args()

    job_dict, order = generate_dict_and_order(args.filename)

    flow = list(job_dict.values())[0]["workflow_name"]

    request_json = ret.copy()
    request_json["parameters"] = generate_params(job_dict)

    sum_calculated = 0
    sum_predicted = 0

    for job in job_dict.keys():
        start = time.perf_counter()
        response = requests.get(f"http://{args.server}/{flow}/predict/{job}/", json=request_json)
        end = time.perf_counter() - start
        json = response.json()
        response_time = int(json["timedelta"])
        try:
            calculated_time = sum(int(job_dict[node]["processing-time"]) for node in json["path"])
            print(f"{job}: {response_time}, {calculated_time}, error: {abs(100*(response_time-calculated_time)/response_time):.03f}")

        except KeyError as e:
            print(f"{job}: {response_time}, couldn't calculate time, key missing: {e.args[0]}")

        except ZeroDivisionError:
            print(f"{job}: {response_time}, {calculated_time}")

        else:
            sum_calculated += calculated_time
            sum_predicted  += response_time

    print(f"Overall error = {abs(100*(sum_calculated-sum_predicted)/sum_calculated)}")