from typing import Dict,List,Callable,Union
import networkx as nx
from .graph_functions import nodes_graph,model_graph,graph_subcomponent_nodes,check_acyclicity
from .model_node import ModelNode

class Model():
    nodes: Dict[str,Callable]
    nodes_graph: nx.DiGraph
    graph: nx.DiGraph
    inputs: List[str]
    call_order: List[str]
    model_nodes: Dict
    auxiliary_nodes:List[str]

    def __init__(self,nodes:Dict[str,Callable]):
        self.nodes = nodes
        self.nodes_graph = nodes_graph(nodes)
        self.graph = model_graph(self.nodes_graph,self.nodes)
        self.inputs = list(set(self.nodes_graph.nodes()).difference(nodes.keys()))
        self.call_order = [node for node in list(nx.topological_sort(self.graph)) if node not in self.inputs]
        self.model_nodes = {node_name:ModelNode(node_name,self.nodes,self.graph) for node_name in self.call_order}
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
    



