import networkx as nx
from typing import Dict,List,Callable
from .helpers import func_args

class ModelNode():
    compute:Callable
    inputs: List

    def __init__(self,node_name:str,nodes:Dict,graph:nx.DiGraph):
        if node_name in nodes.keys() and hasattr(nodes[node_name],"forced_nodes"):
            self.compute = nodes[node_name]
            origin_inputs = func_args(self.compute)
            inputs_unordered = list(graph.predecessors(node_name))
            inputs_dict = {(k[0] if isinstance(k,tuple) else k):k for k in inputs_unordered}
            self.inputs = [inputs_dict[k] for k in origin_inputs]
        elif node_name in nodes.keys():
            self.compute = nodes[node_name]
            self.inputs = func_args(self.compute)
        elif isinstance(node_name,tuple) and len(node_name) == 2:
            self.compute = lambda x = node_name[1]: x
            self.inputs = []
        elif isinstance(node_name,tuple) and len(node_name) > 2:
            origin_node_name = node_name[0]
            self.compute = nodes[origin_node_name]
            origin_inputs = func_args(self.compute)
            inputs_unordered = list(graph.predecessors(node_name))
            inputs_dict = {(k[0] if isinstance(k,tuple) else k):k for k in inputs_unordered}
            self.inputs = [inputs_dict[k] for k in origin_inputs]