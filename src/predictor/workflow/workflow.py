from datetime import datetime
from itertools import chain
from typing import TYPE_CHECKING, Dict, Sequence, Tuple

import networkx as nx

if TYPE_CHECKING:
    from .model import ModelBank
    from .types import Model

from . import logger

logger = logger.getChild("workflow")


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
            # FIXME: remove next line when proper model loading has been implemented
            model = self.bank.load(item)

            self.nodes[item] = model
            self.graph.add_node(item, model=model, name=item)
        self.graph.add_edges_from(connections)

    def find_max(self, target: str) -> float:
        predecessors = list(self.graph.predecessors(target))
        # logger.debug(f"Now traversing: {target}")
        if len(predecessors) > 1:
            return max([self.find_max(i) for i in predecessors]) + self.bank[target].predict()
        elif len(predecessors) == 1:
            return self.find_max(predecessors[0]) + self.bank[target].predict()
        else:
            return self.bank[target].predict()

    def predict(self, target: str, finished: Dict[str, datetime], running: Dict[str, datetime]) -> float:
        if target not in self.nodes:
            logger.critical(f"Target node '{target}' not found in {self.name} workflow!")
            raise AttributeError(f"{target} not found in graph")

        proper_nodes = set()

        for node in chain(finished.keys(), running.keys()):
            if node in self.nodes:
                proper_nodes.add(node)
            else:
                logger.warning(f"Node '{node}' not found in {self.name} workflow")

        return self.find_max(target)

        #    B - C
        #   /     \
        # A        G - H - I
        #   \     /   /
        #    D - E - F
        # what if we have information about G but none about E nor C?
        # the data we got from that csv says that sometimes we dont have
        # all the necessary information (parent_uid randomly drops for example)
        # for now, this simple algorithm must not worry about these possibilities

        # TODO: look for a faster algorthm
        # i'll have to look for a efficient algorithm to do this, so for now:
        #   1. look through all of the target node predecessors until no
        #      predecessor has left
        #   2. for generated in that way path select max of choosing a given path
