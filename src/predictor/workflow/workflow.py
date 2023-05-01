from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Dict, Optional, Sequence, Tuple

import networkx as nx

if TYPE_CHECKING:
    from .model import ModelBank
    from .types import Model

from . import logger

logger = logger.getChild("workflow")


class CurrentNodeStatus(Enum):
    WAITING = "waiting"
    PROCESSING = "processing"
    DONE = "done"


@dataclass
class NodeStatus:
    started: Optional[datetime] = None
    finished: Optional[datetime] = None
    time: float = 0.0
    status: CurrentNodeStatus = CurrentNodeStatus.WAITING

    @classmethod
    def from_finished(cls, finished: datetime):
        return cls(finished=finished, status=CurrentNodeStatus.DONE)

    @classmethod
    def from_running(cls, started: datetime):
        return cls(started=started, status=CurrentNodeStatus.PROCESSING)

    def data(self):
        if self.started:
            return


class Workflow:
    name: str
    graph: nx.DiGraph
    nodes: Dict[str, "Model"]
    bank: "ModelBank"

    def __init__(
        self, name: str, nodes: Sequence[str], connections: Sequence[Tuple[str, str]], model_bank: "ModelBank"
    ) -> None:
        self.name = name
        self.graph = nx.DiGraph()
        self.bank = model_bank
        self.nodes = {}
        for item in nodes:
            model = self.bank[item]

            self.nodes[item] = model
            self.graph.add_node(item, model=model, name=item)
        self.graph.add_edges_from(connections)

    @classmethod
    def find_all_paths(cls, graph: nx.DiGraph, target: str):
        # https://stackoverflow.com/a/59952402
        predecessors = list(graph.predecessors(target))
        if len(predecessors) == 0:
            return [[target]]
        paths = []
        for node in predecessors:
            for v_path in cls.find_all_paths(graph, node):
                paths.append([target] + v_path)
        return paths

    def predict(self, target: str, finished: Dict[str, datetime], running: Dict[str, datetime]) -> float:
        if target not in self.nodes:
            logger.critical(f"Target node '{target}' not found in {self.name} workflow!")
            raise KeyError(f"{target} not found in graph")

        #    B - C
        #   /     \
        # A        G - H - I
        #   \     /   /
        #    D - E - F
        # what if we have information about G but none about E nor C?
        # the data we got from that csv says that sometimes we dont have
        # all the necessary information (parent_uid randomly drops for example)
        # TODO: look for a faster algorthm

        node_status = defaultdict(NodeStatus)

        for node, finish_time in finished.items():
            if node in self.nodes:
                node_status[node] = NodeStatus.from_finished(finish_time)
            else:
                logger.warning(f"Node '{node}' not found in '{self.name}' workflow")

        for node, start_time in running.items():
            if node in self.nodes:
                node_status[node] = NodeStatus.from_running(start_time)
            else:
                logger.warning(f"Node '{node}' not found in '{self.name}' workflow")

        all_paths = self.find_all_paths(self.graph, target)
        all_nodes = set()
        for path in all_paths:
            all_nodes.update(path)

        now = datetime.now()

        for node in all_nodes:
            if node_status[node].status == CurrentNodeStatus.DONE:
                node_status[node].time = 0

            elif node_status[node].status == CurrentNodeStatus.PROCESSING:
                duration = (now - node_status[node].started).total_seconds()
                prediction = self.bank[node].predict()
                duration_left = prediction - duration
                if duration_left < 0:
                    logger.info(f"Node '{node}' exceded predicted time of {duration:.2f} by {-duration_left:.2f}!")
                    duration_left = 0

                node_status[node].time = duration_left

            else:
                for requirement in self.graph.predecessors(node):
                    if node_status[requirement].status != CurrentNodeStatus.WAITING:
                        logger.info(f"Node '{node}' waiting on '{requirement}'")
                node_status[node].time = self.bank[node].predict()

        longest_path = 0
        path_lengths = [sum([node_status[j].time for j in i]) for i in all_paths]
        for i, path in enumerate(path_lengths):
            if path > path_lengths[i]:
                longest_path = i

        # return {i: sum([node_status[j].time for j in k]) for (i, k) in enumerate(all_paths)}
        return all_paths[longest_path], path_lengths[longest_path]