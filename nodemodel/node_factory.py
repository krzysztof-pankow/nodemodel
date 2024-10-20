from typing import Dict,List,Callable
from types import FunctionType
from .helpers import func_args

class Node():
    compute:Callable
    inputs: Dict[str,str]
    def __init__(self,node:FunctionType):
        self.compute = node
        self.inputs = {k:k for k in func_args(node)}

def node_factory(function_nodes:Dict[str,Callable])-> Dict[str, Node]:
    nodes = {}
    for node_name,node in function_nodes.items():
        if hasattr(node,"node_cases"):
            generated_nodes = generate_nodes(node_name,node)
            nodes.update(generated_nodes)
        else:
            nodes[node_name] = Node(node)
            if hasattr(node,"forced_nodes"):
                nodes[node_name].forced_nodes = node.forced_nodes
    return nodes

def generate_nodes(node_name:str,node:Callable)-> Dict[str, Node]:
    nodes = {}
    for node_case in node.node_cases:
        node_template = node   
        nodes[getattr(node_case,node_name)] = node_generator(node_template,node_case)
    return nodes

def node_generator(node_template:Callable,node_case:object)-> Node:
    node = Node(node_template)
    node.inputs = generate_inputs(node.inputs,node_case)
    return node

def generate_inputs(inputs_template:Dict[str,str],node_case:object)->Dict[str,str]:
    inputs = inputs_template
    for k in inputs.keys():
        if hasattr(node_case,k):
            inputs[k] = getattr(node_case,k)
    return inputs