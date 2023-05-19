import argparse
import os

parser = argparse.ArgumentParser("workflow-predictor", description="Start development server or train weights.")
parser.add_argument("action", choices=["serve", "learn"])
parser.add_argument("--job", "-j", dest="job", help="Which job to train? Defaults to all")
parser.add_argument(
    "--calculated", "-c", default="data/maestro-calculated.csv", dest="calculated", help="Path to precalculated csv"
)
parser.add_argument(
    "--task-column-def",
    "-t",
    default="data/task-columns.yml",
    dest="task_column",
    help="Path to file containing task to columns associations",
)
parser.add_argument("--dest", "-d", default=os.getcwd(), dest="destination", help="Where to save model files?")
parser.add_argument("--epochs", "-e", default=20, type=int, dest="epochs", help="Amount of epochs to run")
parser.add_argument("--batch", "-b", default=2, type=int, dest="batch_size", help="Model batch size")
parser.add_argument(
    "--production",
    "-p",
    default=False,
    action="store_true",
    dest="split",
    help="Whether to split learning dataset into validation and learn",
)

if __name__ == "__main__":
    parsed = parser.parse_args()

    if parsed.action == "serve":
        from predictor import get_app

        get_app().run("0.0.0.0", 5000, debug=False, load_dotenv=True)
    elif parsed.action == "learn":
        from learn import ModelLearn

        learner = ModelLearn(parsed.calculated, parsed.task_column, parsed.destination)
        if parsed.job:
            learner.learn_single(parsed.job, not parsed.split, batch_size=parsed.batch_size, epochs=parsed.epochs)
        else:
            learner.learn(not parsed.split, batch_size=parsed.batch_size, epochs=parsed.epochs)
