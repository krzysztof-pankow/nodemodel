from typing import Dict,List,Callable
from types import FunctionType
from .helpers import func_args

class Node():
    compute:Callable
    inputs: List[str]
    def __init__(self,node:FunctionType):
        self.compute = node
        self.inputs = func_args(node)

def node_factory(nodes:Dict[str,Callable])-> Dict[str, Node]:
    new_nodes = {}
    for node_name,node in nodes.items():
        new_node = Node(node)
        if hasattr(node,"forced_nodes"):
            new_node.forced_nodes = node.forced_nodes
        new_nodes[node_name] = new_node
    return new_nodes
