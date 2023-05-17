import sys

from learn import ModelLearn
from predictor import get_app

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("[ERROR] run mode not specified")
        exit(-1)

    if sys.argv[1] == "serve":
        get_app().run("0.0.0.0", 5000, debug=False, load_dotenv=True)
    elif sys.argv[1] == "learn":
        ModelLearn("data/maestro-calculated.csv", "data/task-columns.yml", "/tmp/models/").learn()

    else:
        print(f"unknown parameter '{sys.argv[1]}'")
