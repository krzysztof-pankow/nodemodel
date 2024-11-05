import networkx as nx
from typing import Dict,Union,Tuple,Callable
from collections.abc import Hashable
from .helpers import callable_args


class Node:
    """Represents a computation node in a graph.

    This class wraps a callable and tracks its inputs, which are 
    the arguments of the callable. The inputs can be extended by 
    the 'inputs' attribute of the callable if it exists.

    Args:
        node (Callable): The callable object that represents the node's computation.
    """
    def __init__(self,node:Callable):
        self.compute = node
        self.inputs = {k:k for k in callable_args(node)}
        if hasattr(node,"inputs"):
            self.inputs.update(node.inputs)

class NodeForcedToValue:
    """A node that returns a fixed hashable value.

    This node is initialized with a hashable value and will always 
    return this value when computed.

    Example:
        node_name = ('a', 5)  # This node will always return 5.
    
    Args:
        forced_node_value (Hashable): The value that the node is forced to return.
    """
    def __init__(self,forced_node_value:Hashable):
        self.compute = lambda x = forced_node_value: x
        self.inputs = {}

class NodeForcedToNode:
    """A node that returns the output of another node.

    This node is initialized with a tuple specifying another node 
    and will return its input when computed.

    Example:
        node_name = ('a', ('node', 'b'))  # This node will return the output of node 'b'.
    
    Args:
        forced_node_value (Hashable): A tuple where the second element is the name of the node to return.
    """
    def __init__(self,forced_node_value:Hashable):
            self.compute = lambda x : x
            self.inputs = {"x":forced_node_value[1]}

class NodeWithForcedNodes:
    """A node that may have forced nodes as inputs.

    This node can either have a `forced_nodes` attribute or be 
    connected to other nodes that have this attribute. It requires 
    the inputs to be derived from the predecessors in the computation 
    graph.

    Example:
        node_name = 'a' and a.forced_nodes = {"x": 1}
        node_name = ('c', 'x', 1)
    
    Args:
        node_name (Union[str, Tuple]): The name of the node, which may be a string or a tuple.
        nodes (Dict[str, Node]): A dictionary mapping node names to Node instances.
        graph (nx.DiGraph): A directed graph representing the structure of the computation model.
    """
    def __init__(self,node_name:Union[str, Tuple],nodes:Dict[str,Node],graph:nx.DiGraph):
        origin_node_name = node_name if isinstance(node_name,str) else node_name[0]
        origin_node =  nodes[origin_node_name]
        self.compute = origin_node.compute
        node_predecessors = list(graph.predecessors(node_name))
        inputs_mapping = {(k[0] if isinstance(k,tuple) else k):k for k in node_predecessors}
        self.inputs = {k:inputs_mapping[v] for k,v in origin_node.inputs.items()}


def node_factory(node_name:Union[str, Tuple],nodes:Dict[str,Node],graph:nx.DiGraph):
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
        return NodeWithForcedNodes(node_name,nodes,graph)
    elif isinstance(node_name,str):
        return nodes[node_name]
    elif isinstance(node_name,tuple) and len(node_name) == 2:
        forced_node_value =  node_name[1]
        if isinstance(forced_node_value,tuple) and len(forced_node_value) == 2 and forced_node_value[0] == "node":
            return NodeForcedToNode(forced_node_value)
        else:
            return NodeForcedToValue(forced_node_value)
    elif isinstance(node_name,tuple) and len(node_name) > 2:
        return NodeWithForcedNodes(node_name,nodes,graph)
    