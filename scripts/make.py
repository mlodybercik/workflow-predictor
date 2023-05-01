import os
import sys
from pathlib import Path

current_dir = Path(os.getcwd()).absolute()

if current_dir.name != "workflow-predictor":
    print(f"Unknown location {current_dir}")
    if current_dir.parent.name != "workflow-predictor":
        print("Unknown structure exiting")
        exit(-1)
    print(f"Changing to root {current_dir.parent}")
    os.chdir(current_dir.parent)

print("Executing scripts/clean_data.py")
if os.system("python scripts/clean_data.py"):
    exit(-1)

print("Executing scripts/get_times.py")
if os.system("python scripts/get_times.py"):
    exit(-1)

print("done, have a nice day :)")

