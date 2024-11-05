from typing import Dict,List,Callable,Union
import networkx as nx
from .graph_functions import nodes_graph,model_graph
from .node import Node,node_factory
from .helpers import call_inputs


class Model:
    """
    Represents a directed acyclic graph (DAG) of callable objects, where each node is a callable, and edges depict 
    input-output relationships between these objects.

    The `Model` class creates and manages a computational graph in which nodes are any callable objects (e.g., functions, 
    objects with a `__call__` method) that may depend on the outputs of other nodes. Dependencies are automatically determined 
    based on callable argument names, enabling the model to construct and execute functions in the appropriate order 
    based on their input requirements.

    Additionally, dependencies can be modified by setting an `inputs` property on a callable **before** it is passed 
    into the `Model` initializer. By default, each node's arguments map directly to other nodes with matching names. 
    However, users can override this by setting `inputs` on the callable as a dictionary, where keys are the callable's 
    argument names and values specify alternative nodes to use as inputs. For example, setting `node.inputs = {"a": "b"}` 
    on a callable would map the argument `a` to the output of node `b`. This modification must be applied **before** 
    passing the callable into the `Model.__init__()` method.

    Attributes:
        nodes (Dict[str, Node]): A dictionary with node names as keys and corresponding `Node` objects as values, 
            representing callables within the graph.
        nodes_graph (nx.DiGraph): A directed acyclic graph representing the direct input-output relationships between 
            nodes (callables).
        graph (nx.DiGraph): A directed acyclic graph of the entire model, including auxiliary nodes and representing 
            all dependencies.
        inputs (List[str]): A list of node names that act as input values; these nodes have no dependencies within the model.
        call_order (List[str]): The topologically sorted list of node names representing the execution order for the model.
        model_nodes (Dict[str, model_node]): A dictionary mapping node names to their respective `model_node` instances, 
            which handle the computational logic of each node.
        auxiliary_nodes (List[str]): Nodes created within the graph as auxiliary nodes, typically required for conditional functions.
    """
    
    def __init__(self, nodes: Dict[str, Callable]):
        """
        Initializes a `Model` instance, building the graph and preparing nodes for computation.

        The `__init__` method constructs a directed acyclic graph (DAG) from a dictionary of nodes, where each node 
        is a callable object (e.g., function or an instance of a class with a `__call__` method) that may depend on other 
        nodes' outputs. Dependencies are inferred from the arguments of each callable, creating edges in the graph for each 
        dependency. 

        By default, each callable’s arguments map to nodes with matching names in the graph. To customize dependencies, 
        users can add an `inputs` attribute to a callable **before** it is passed into `Model.__init__()`. This `inputs` 
        attribute should be a dictionary mapping the callable’s argument names to alternative nodes in the model. 
        For example, setting `node.inputs = {"a": "b"}` on a callable will map its `a` argument to the output of node `b`. 

        The method identifies input nodes, determines an execution order through topological sorting, and 
        initializes `model_node` objects for each node to facilitate computations.

        Args:
            nodes (Dict[str, Callable]): 
                A dictionary where each key is a node name and each value is a callable (such as a function or callable object) 
                that may depend on the outputs of other nodes. The arguments of each callable define its dependencies.
        """
        self.nodes = {node_name: Node(node) for node_name, node in nodes.items()}
        self.nodes_graph = nodes_graph(self.nodes)
        self.graph = model_graph(self.nodes_graph, self.nodes)
        self.inputs = list(set(self.nodes_graph.nodes()).difference(self.nodes.keys()))
        self.call_order = [node for node in list(nx.topological_sort(self.graph)) if node not in self.inputs]
        self.model_nodes = {node_name: node_factory(node_name, self.nodes, self.graph) for node_name in self.call_order}
        self.auxiliary_nodes = list(set(self.graph.nodes()).difference(self.nodes_graph.nodes()))


    def compute(self,input:Dict,keep_auxiliary_nodes:bool=False,**kwargs)->Dict:
        """
        Executes the model's computations in topological order, updating the input dictionary with the results.

        This method iteratively computes each function in the model using values from the `input` dictionary. 
        The computation follows the topological order of the model's graph (`self.call_order`), ensuring that 
        each node's dependencies are resolved before it is computed. Additional keyword arguments can be provided 
        to temporarily add data to the `input` dictionary during computation.

        Args:
            input (Dict): A dictionary containing initial input values for the model. It will be updated 
                in-place with the results of each computed node in the model.
            keep_auxiliary_nodes (bool, optional): If True, retains auxiliary nodes computed for conditional 
                functions in the final `input` dictionary. If False, auxiliary nodes are removed after 
                computation. Defaults to False.
            **kwargs: Additional key-value pairs to be added temporarily to the `input` dictionary during 
                computation. These are removed after computation is complete.

        Returns:
            Dict: The updated `input` dictionary, now containing entries for each computed function in the model.

        Example:
            >>> model = Model(nodes)  # Assume `Model` is initialized with a set of nodes
            >>> result = model.compute(input_data, keep_auxiliary_nodes=True, extra_param=42)
            >>> # `result` now contains values for all nodes computed according to the model graph
        """
        input.update(kwargs)
        for node_name in self.call_order:
            model_node = self.model_nodes[node_name]
            input[node_name] = model_node.compute(**call_inputs(input,model_node.inputs))
        if not keep_auxiliary_nodes:
            for auxiliary_node in self.auxiliary_nodes:
                del input[auxiliary_node]
        for k in kwargs.keys():
            del input[k]
        return input
    
    def submodel(self, nodes_names: Union[str, List[str]]) -> 'Model':
        """Generates a submodel containing specified nodes and their ancestor nodes.

        This method creates a submodel by including the specified nodes along with 
        all their ancestor nodes in the model's dependency graph. The resulting 
        submodel preserves the structure and functionality of the original model 
        but is limited to the specified nodes and their dependencies.

        Args:
            nodes_names (Union[str, List[str]]): A single node name or a list of node names 
                whose ancestors should be included in the submodel.

        Returns:
            Model: A new `Model` instance representing the submodel, which includes 
            the specified nodes and all their ancestors from the original model.

        Example:
            >>> submodel = model.submodel(['node_a', 'node_b'])
            >>> # `submodel` includes 'node_a', 'node_b', and all nodes that are 
            >>> # ancestors of 'node_a' or 'node_b' in the dependency graph.
        """
        nodes_names = [nodes_names] if isinstance(nodes_names, str) else nodes_names
        subcomponent_nodes_names = set()
        for node_name in nodes_names:
            subcomponent_nodes_names.update(nx.ancestors(self.nodes_graph, node_name))
        subcomponent_nodes_names.update(nodes_names)
        submodel_nodes = {node_name:node.compute for node_name,node in self.nodes.items() if node_name in subcomponent_nodes_names}
        submodel = Model(submodel_nodes)
        return submodel
