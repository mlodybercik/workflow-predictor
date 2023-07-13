# workflow-predictor
Team Engineering Project, project for Credit Suisse (rip). ("""Team""", backend and research made only by me 🤷‍♀️)

## What does it do?
This project aims to create an tool for predicting time of DAG, action on node, workflows by predicting the time of each node and choosing the longest path to given node. This tool can:
- create different kind of prediction models in very granular way used for time estimation,
- serve an API that can be used to query given node in given workflow to get the time estimation.

## Who is this for?
psychopats as far as I'm concerned 🤷‍♀️

---

If you deal with long task pipelines that take different amounts of time based on some given apriori parameters and you want to have an app that can be used to at least get an estimation based on current state of execution graph, then it's for you.

**This implementation does not take into account execution times of other nodes. We assume that the time does not depend on execution time of previous nodes but only on submitted parameters** (input data could be structured in that way that could take those values into consideration, but API isn't ready for that in any way), we also assume that time between tasks (if all of the predecessors end) is insignificant.



## Development
This project uses `pipenv` so it's the first and most important thing you'll need. I use python 3.9, because of my addiction to walrus `:=` and some QOL methods in standard library. `Tensorflow` is locked to `2.11` because of my old GPU I have in my homelab that accelerates the Deep Learning part of the project. Project is mainly built to be run in Linux Docker containers, but there is option for baremetal. I use `pre-commit` for code quality maintainment.
To set the environment up:
```bash
python3 -m pip install pipenv
pipenv install --dev
pipenv shell
pre-commit install
```

## Starting
### Learning
To start the learning process you have to have the files provided by Credit Suisse, but the code is (almost) made for accepting any kind of properly formatted data (maybe in the future, I'll make a propper source-agnostic data format). You shoud have:
- files describing some kind of a workflow, (directed acyclic graph to be precise with action on node, not on an edge)
- raw input data (as I said above, maybe in the future I'll change format of the input data to be more standard'ish cos for now only data we have is kinda private from Credit Suisse)

Place them into `data/` directory, and run `python scripts/make.py`. It'll format and extract all the data we need for learning process.

Next, we have to start the learning process. We can - in very granular way - change how we process each task by passing different basic parameters to learning script `... learn --batch 8 --epochs 15 --job <job-name>`, or we could change more advanced settings like model shape, the optimizer or time mapping functions by editing `learn/model_mapping.py` file (you could even use convolution if you really wanted to). After the deep learning stage, model is serialized with all the neccesary data to convert mapped time back into real time used in estimation.

Before the deep learning stage, every parameter for each task (separately) is checked, how does it influence the mean execution time of that perticular task. We generate list of parameter keys sorted by resulting mean with that perticular parameter value. Each value in that list gets assigned number from -1 to 1. (-1 when average is the lowest for that parameter and 1 for max) and we give those values to inputs of each model (**if some parameter has not been seen with a given task, we assume that it doesn't influence the mean execution time**). This could be good for lots of parameters that hugely influence the mean value, but not necessarily when having lots of similar values and then few outliers. This could be easily dealt with though.

---

#### Script usage:
By default, it will search for neccesary files inside the `data/` directory, you could invoke the script with `-h` to get all of the learning params.

`python src/app.py -d <destination> learn -b 8 -e 20 -p -j open-date-card`

### Backend
After getting yourself trained or pretrained models you can start the API. You will need these models alongside the workflows definitions to start the backend. By default it looks for directories in `/tmp/` that contain the graph definitions and model definitions. (`/tmp/workflows/` and `/tmp/models/`). Inside the first one it looks for `.yml` files with propper structure (in the future™ ill make the structure more standard), and in the second one, it looks for custom `.wfp` files with model definitions.

To start the backend server:
- if you use Docker: `docker compose build`, `docker compose up` and to tear down, `docker compose down`
- if you don't use Docker or you are prototyping and don't want to rebuild the image every 15 seconds: `python src/app.py`.

#### Script usage:
`TASK_COLUMNS_LOCATION=data/task-columns.yml MODEL_DEFINITIONS_LOCATION=../workflow-models/ python src/app.py serve`

### API
Backend creates *single* endpoint for every workflow definition `<workflow-name>/predict/<target-node>/` used for communication.

Request structure is as follows:
```json
{
    "processing": {
        // currently executing nodes, we pass the task identifier (its name) as a key
        // and epoch time of the beggining as value
        "make-a-sandwich": 1112729820
    },
    "done": {
        // same as the above, but epoch time of finishing the task
        "task-a": 1112729800,
        "task-b": 1112729700
    },
    "parameters": {
        // we pass all of the parameters for given task here with key as its name and value as its value
        // you can skip parameters for tasks that are done, they wont be used to predict either way
        "make-a-sandwich": {"param-a": 72, "param-b": "with_bread"}
    }
}
```
#### Example
```bash
$ curl -X GET -H 'Content-Type: application/json' -d '<big-json-here>' http://localhost:5000/strategic-flow/predict/reload-b3-tables/
{"path": ["node1", "node2", ..., "nodeN_in_path"], "timedelta": 2137.69420}
```

## Things to be improved/changed
1. BIG ~~klamoty~~ REQUESTS. If users wants to know time estimation of an task that has a long path, user has to send huge json requests (multiple kb in size). We could mitigate some of that problem by adding another field in request structure that would contain common parameters for all of the tasks that would be overwritten by non-default parameters in `parameters` field.

2. Request handling could be sped up by using Redis or LRU cache, when user often sends similar requests with similar generated paths. If node `A` has been predicted with set of parameters `a` in one request, those can be used in another request if user requests another path that goes through node `A` with the same parameters. In testing, we could achieve (in rather big workflow, >20 path length) about 10x speed improvement just by adding `@lru_cache`. For now, its enabled.

3. Currently in learning preamble, we reduce amount of parameters by checking if more than one (other than null) parameter exists, then for every existing value for that parameter we calculate how does it influence mean for that task. We sort those parameters by mean and map those values ***uniformly*** from -1 to 1. Then we map every task like that and use those values to teach the deep learning models. We save this list (without the values, just the order) in `.wfp` files, and then use the same algorithm to recreate the mapping when deserializing models. The issue is we assume that every parameter influences the mean and every other parameter value in order influences the mean by constant value. This can't be this easy. We should calculate the ratio to mean in whole set and then save the mapping without the need to recalculate it after deserializing. We could even go as far as mapping those ratios to values between -1 and 1  Now we do:
```python
ordered_params = {'S': -0.5, 'I': -0.4, 'J': -0.3, 'K': -0.2, 'R': -0.1, 'P': 0.0, 'O': 0.1, 'N': 0.2, 'M': 0.3, 'L': 0.4}
# but this in reality could very much be as follows
ordered_params = {'S': -0.78, 'I': -0.76, 'J': -0.72, 'K': 0.0, 'R': 0.01, 'P': 0.02, 'O': 0.75, 'N': 0.78, 'M': 0.82, 'L': 0.83}
```
In case of receiving a parameter that we don'h have in our mapping, we could surgically add this value to json in `<model_file>.wfp/meta.json` without re-learning the whole dataset.

4. We rely on the fact that we can teach our models in advance on a big set of parameters but what if we could have a functionality to collect those parameters for future use? 🤔 Also, we could store some statistics about executed tasks, after receiving data about real time.
5. We don't need to have loaded all models in memory at all times, as those models aren't that big, we could just lazy-load them.
6. We assume that infinite amount of tasks can be executing at the same time. We could add some kind of smart-ish de-queuer that would give us worst and best case scenario for given path that has to execute more tasks than the system is capable, or we could give it the scheduling rules to get propper estimations.
7. When in production we don't want to restart the whole system just to add new or update models/workflows. We could have some kind of admin endpoint that would make system soft-restart, dropping all models, caches, workflows and reloading them from disk.
8. Redo the pathfinding algorithm 🙈🙊🙉
