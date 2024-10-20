import networkx as nx
from typing import Dict,Union, Tuple
from collections.abc import Hashable
from .node_factory import Node

class ModelNodeWithForcedNodes(Node):
    """
    A node with the 'forced_nodes' attribute.
    Example: node_name = 'a' and a.forced_nodes = {"x":1}
    """
    def __init__(self,node_name:str,nodes:Dict[str,Node],graph:nx.DiGraph):
        self.compute = nodes[node_name].compute
        node_predecessors = list(graph.predecessors(node_name))
        self.inputs = {(k[0] if isinstance(k,tuple) else k):k for k in node_predecessors}
        self.inputs = {k:v for k,v in self.inputs.items() if k in nodes[node_name].inputs.keys()}

class ModelNodeForcedToValue(Node):
    """
    A node forced to a hashable value.
    Example: node_name = ('a',5)
    """
    def __init__(self,forced_node_value:Hashable):
        self.compute = lambda x = forced_node_value: x
        self.inputs = {}

class ModelNodeForcedToNode(Node):
    """
    A node forced to another node.
    Example: node_name = ('a',('node','b'))
    """
    def __init__(self,forced_node_value:Hashable):
            self.compute = lambda x : x
            self.inputs = {"x":forced_node_value[1]}

class ModelNodeRecalculatedWithForcedNodes(Node):
    """
    A node that is an ancestor of a node with the 'forced_nodes' attribute and also a successor of the nodes in its 'forced_nodes'.
    Example: node_name = ('c','x',1)
    """
    def __init__(self,node_name:Tuple,nodes:Dict[str,Node],graph:nx.DiGraph):
        origin_node_name = node_name[0]
        self.compute = nodes[origin_node_name].compute
        node_predecessors = list(graph.predecessors(node_name))
        self.inputs = {(k[0] if isinstance(k,tuple) else k):k for k in node_predecessors}


def model_node_factory(node_name:Union[str, Tuple],nodes:Dict[str,Node],graph:nx.DiGraph):
    """
    A factory function that selects the appropriate `Node` class based on the given `node_name`.

    This function constructs objects whose `compute` method will be invoked iteratively 
    within the `Model.compute` method. These objects represent nodes in the computation 
    graph.
    
    Args:
        node_name (Union[str, tuple]): The name of the node, as defined when constructing the graph using 
            the `model_graph` function.
        nodes (Dict[str,Callable]): A dictionary of functions included in the model.
        graph (nx.DiGraph): A directed graph (DiGraph) representing the structure of the model, 
            created from the `nodes` dictionary.

    Returns:
        Node: An instance of a class inheriting from `Node`.
        The returned object has the following proporties
        - `compute`: A method used to perform computations at the node.
        - `inputs`: The inputs required for the node's computation.
    """
    if node_name in nodes.keys() and hasattr(nodes[node_name].compute,"forced_nodes"):
        return ModelNodeWithForcedNodes(node_name,nodes,graph)
    elif isinstance(node_name,str):
        return nodes[node_name]
    elif isinstance(node_name,tuple) and len(node_name) == 2:
        forced_node_value =  node_name[1]
        if isinstance(forced_node_value,tuple) and len(forced_node_value) == 2 and forced_node_value[0] == "node":
            return ModelNodeForcedToNode(forced_node_value)
        else:
            return ModelNodeForcedToValue(forced_node_value)
    elif isinstance(node_name,tuple) and len(node_name) > 2:
        return ModelNodeRecalculatedWithForcedNodes(node_name,nodes,graph)
    