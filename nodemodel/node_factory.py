from typing import Dict,List,Callable
from types import FunctionType
from .helpers import func_args,copy_func

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
    return nodes

def generate_nodes(node_name:str,node:Callable)-> Dict[str, Node]:
    nodes = {}
    for node_case in node.node_cases:
        nodes[getattr(node_case,node_name)] = node_generator(node,node_case)
    return nodes

def node_generator(node_template:Callable,node_case:object)-> Node:
    node = Node(node_template)
    node.inputs = generate_inputs(node.inputs,node_case)
    node.compute = generate_compute(node.compute,node_case)
    return node

def generate_inputs(inputs_template:Dict[str,str],node_case:object)->Dict[str,str]:
    inputs = inputs_template
    for k in inputs.keys():
        if hasattr(node_case,k):
            inputs[k] = getattr(node_case,k)
    return inputs

def generate_compute(compute_template:FunctionType,node_case:object)->FunctionType:
    compute = copy_func(compute_template)
    compute.__name__ = getattr(node_case,compute_template.__name__)
    for var in compute_template.__code__.co_names: #global variables of compute_template
        if hasattr(node_case,var):
            compute.__globals__[var] = getattr(node_case,var)
    if hasattr(node_case,"forced_nodes"):
        compute.forced_nodes = getattr(node_case,"forced_nodes")
    return compute
