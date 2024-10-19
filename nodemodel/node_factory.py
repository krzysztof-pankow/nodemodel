from typing import Dict,List,Callable
from types import FunctionType
from .helpers import func_args

class Node():
    compute:Callable
    inputs: List[str]
    def __init__(self,node:FunctionType):
        self.compute = node
        self.inputs = func_args(node)

def node_factory(function_nodes:Dict[str,Callable])-> Dict[str, Node]:
    nodes = {}
    for node_name,node in function_nodes.items():
        nodes.update(node_generator(node_name,node))
    return nodes

def node_generator(node_name:str,node:Callable)-> Dict[str, Node]:
    nodes = {}
    if hasattr(node,"node_cases"):
        node_template = Node(node)
        for node_case in node.node_cases:
            new_node = Node(node)
            new_node_name = getattr(node_case,node_name)
            #TO DO: Change nodes names
            nodes[new_node_name] = new_node
    else:
        nodes[node_name] = Node(node)
        if hasattr(node,"forced_nodes"):
            nodes[node_name].forced_nodes = node.forced_nodes
    return nodes


