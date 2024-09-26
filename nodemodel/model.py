from typing import Dict,List,Callable,Union
import networkx as nx
from .graph_functions import nodes_graph,model_graph,graph_subcomponent_nodes,check_acyclicity
from .model_node import model_node_factory

class Model():
    """
    A class for creating and processing a directed acyclic graph (DAG) of functions, where the nodes are functions and 
    the edges represent the relationships between the function inputs and outputs.

    The `Model` class is designed to handle a computational graph where each node is a function that depends on the outputs
    of other functions (nodes) in the graph. It uses the names of the functions and their argument names to automatically 
    construct the graph, defining dependencies between functions and their inputs.

    Attributes:
        nodes (Dict[str, Callable]): A dictionary where keys are node names and values are functions representing nodes in the graph.
        nodes_graph (nx.DiGraph): A directed acyclic graph (DAG) representing the input-output relationships between the functions.
        graph (nx.DiGraph): A directed acyclic graph (DAG) representing the entire computational model, including auxiliary nodes.
        inputs (List[str]): A list of node names representing input values (nodes without dependencies).
        call_order (List[str]): A list of node names in topological order of execution (excluding inputs).
        model_nodes (Dict[str, model_node]): A dictionary of node names to their respective `model_node` objects, used for computation.
        auxiliary_nodes (List[str]): A list of nodes that are generated as auxiliary nodes in the graph, typically for conditional functions.
    """
    def __init__(self,nodes:Dict[str,Callable]):
        """
        Initializes the `Model` instance by constructing the function graph and preparing the model for computation.

        The method takes a dictionary of node functions, where the keys are the node names and the values are the corresponding 
        functions. It generates a directed acyclic graph (DAG) representing the dependencies between the nodes based on their 
        inputs and outputs. The method identifies input nodes (nodes with no dependencies) and calculates the execution order 
        of the nodes based on a topological sort. Additionally, it prepares `model_node` objects for each node to handle the 
        actual computations.

        Args:
            nodes (Dict[str, Callable]): 
                A dictionary where the keys are the names of the nodes (functions), and the values are the function objects.
                The functions can have dependencies on other nodes, with their arguments corresponding to the outputs of other nodes.
        """
        self.nodes = nodes
        self.nodes_graph = nodes_graph(nodes)
        self.graph = model_graph(self.nodes_graph,self.nodes)
        self.inputs = list(set(self.nodes_graph.nodes()).difference(nodes.keys()))
        self.call_order = [node for node in list(nx.topological_sort(self.graph)) if node not in self.inputs]
        self.model_nodes = {node_name:model_node_factory(node_name,self.nodes,self.graph) for node_name in self.call_order}
        self.auxiliary_nodes = list(set(self.graph.nodes()).difference(self.nodes_graph.nodes()))

    def compute(self,input:Dict,keep_auxiliary_nodes:bool=False,**kwargs)->Dict:
        """
        Computes functions in the model using the input dictionary. The computation is performed in-place, with functions executed iteratively 
        according to the topological order of the model graph (`self.call_order`).

        Args:
            input (Dict): The input dictionary.
            keep_auxiliary_nodes (bool, optional): Whether to retain auxiliary nodes calculated for conditional functions in the dictionary. 
            Defaults to False.
            **kwargs: Additional inputs that will be temporarily added to the dictionary during the calculation and removed afterward.

        Returns:
            Dict: The dictionary with additional entries corresponding to the computed functions in the model.
        """
        input.update(kwargs)
        for node_name in self.call_order:
            model_node = self.model_nodes[node_name]
            call_input = [input[k] for k in model_node.inputs]
            input[node_name] = model_node.compute(*call_input)
        if not keep_auxiliary_nodes:
            for auxiliary_node in self.auxiliary_nodes:
                del input[auxiliary_node]
        for k in kwargs.keys():
            del input[k]
        return input
    
    def submodel(self,nodes_names:Union[str,List[str]]):
        """Returns a submodel of the current model. 
        The new model corresponds to the graph that includes all ancestors of the node_names, along with the node_names themselves.

        Args:
            nodes_names (Union[str,List[str]]): Names of nodes whose ancestors should be included in the submodel.

        Returns:
            Model: The submodel of the  model.
        """
        nodes_names = [nodes_names] if isinstance(nodes_names, str) else nodes_names
        subcomponent_nodes_names = set()
        for node_name in nodes_names:
            subcomponent_nodes_names.update(nx.ancestors(self.nodes_graph, node_name))
        subcomponent_nodes_names.update(nodes_names)
        submodel_nodes = {node_name:node for node_name,node in self.nodes.items() if node_name in subcomponent_nodes_names}
        submodel = Model(submodel_nodes)
        return submodel
    



