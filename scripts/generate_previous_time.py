import csv
import yaml
import numpy as np
import networkx as nx
import re
import sys

from collections import defaultdict
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Dict, Union, Set, Any, DefaultDict

# why colon is not in quote in yaml wtf
PATTERN = re.compile(r"^(\s+[\w-]+: )(.*:.*)$", re.MULTILINE)
METRIC = "event-processing-time"
LOW_QUANTILE = 0.05
HIGH_QUANTILE = 1 - LOW_QUANTILE

ALL_JOBS: Dict[str, "Job"] = dict()
MEAN_TIMES: Dict[str, float] = dict()
JOBS_TYPES: DefaultDict[str, Dict[str, "Job"]] = defaultdict(dict)


@dataclass(repr=False)
class Job:
    uid: str
    parent_uid: Optional[str]
    time: int
    name: str
    _data: Dict[str, Union[int, str]]

    previous_ratio: float = 1.0

    __hash__ = lambda self: hash(self.uid.lower())
    __repr__ = lambda self: f"<{self.__class__.__name__} uid='{self.uid}' p_uid='{self.parent_uid}' time='{self.time}' name='{self.name}'>"

    @property
    def data(self):
        return {**self._data, "previous-ratio": self.previous_ratio}


    @classmethod
    def from_entry(cls: "Job", line: Dict[str, str]) -> "Job":
        uid = line["uid"]
        if (puid := line.get("parent_uid", None)):
            puid = puid.lower()
        return cls(uid=uid.lower(), parent_uid=puid, time=int(line[METRIC]), name=line["job_name"], previous_ratio=1, _data=line)


def open_graph(path: Path):
    with open(path) as file:
        content = ""
        for line in file:
            if(match := PATTERN.match(line)):
                pre, missing_quote = match.groups()
                content += f'{pre}"{missing_quote}"\n'
            else:
                content += line

    graph = nx.DiGraph()
    graph_yaml = yaml.load(content, yaml.Loader)
    for job_pre in graph_yaml["workflows"][0]["jobs"]:
        if (job := job_pre.get("job", None)) or (job := job_pre.get("nop", None)):
            node_name = job.get("name")
            graph.add_node(node_name, name=node_name)
            for precondition in job.get("precondition", []):
                graph.add_edge(node_name, precondition)

    return graph

def main(graph: nx.DiGraph, name: str):
    # first, we have to prepare three dicts, 
    global ALL_JOBS     #  uid -> Job    
    global MEAN_TIMES   #  job_name -> float
    global JOBS_TYPES   #  job_name -> uid -> job

    with open("data/maestro-calculated.csv") as file:
        reader = csv.DictReader(file, lineterminator="\n")
        headers = tuple(reader.fieldnames)

        for line in reader:
            # if not (line["job_name"] in graph.nodes):
            #     continue

            job = Job.from_entry(line)
            ALL_JOBS[job.uid] = job
            JOBS_TYPES[job.name][job.uid] = job
        
        JOBS_TYPES = dict(JOBS_TYPES)

    for job_name in JOBS_TYPES.keys():
        times = np.array([i.time for i in JOBS_TYPES[job_name].values()], dtype=float)
        low_quantile = np.quantile(times, LOW_QUANTILE)
        high_quantile = np.quantile(times, HIGH_QUANTILE)

        MEAN_TIMES[job_name] = times[(times >= low_quantile) & (times <= high_quantile)].mean()

    

    for job_name in JOBS_TYPES.keys():
        for job in JOBS_TYPES[job_name].values():
            if not job.parent_uid:
                continue
            try:
                parent = ALL_JOBS[job.parent_uid]
                if MEAN_TIMES[parent.name] >= 1:
                    job.previous_ratio = float(parent.time / MEAN_TIMES[parent.name])
            except KeyError:
                pass

    parentless = defaultdict(int)
    parentmissing = defaultdict(int)

    # for job_name in JOBS_TYPES.keys():
    for job in JOBS_TYPES["complete-securitization-batch"].values():
        if not job.parent_uid:
            parentless[job.name] += 1
            continue
        try:
            while job.parent_uid:
                job = ALL_JOBS[job.parent_uid]
            parentless[job.name] += 1
        except KeyError:
            parentmissing[job.name] += 1

    print("Parentless:", parentless)
    print()
    print("Parent missing:", parentmissing)
    
                

    with open(f"data/maestro-calculated-{name}.csv", "w") as file:
        writer = csv.DictWriter(file, headers + ("previous-ratio",), lineterminator="\n")
        writer.writeheader()
        writer.writerows((i.data for i in ALL_JOBS.values()))



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("[ERROR]: missing parameter")
        print(f"python {sys.argv[0]} [graph-name]")
        exit(-1)
    name = sys.argv[1]
    path = Path(f"data/{name}.yml")
    if not path.exists():
        print(f"[ERROR]: file 'data/{name}' doesnt exist")
        exit(-1)
    
    main(open_graph(path), name)
    

        
    