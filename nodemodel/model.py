from typing import Dict,List,Callable
import networkx as nx
from .graph_functions import nodes_graph,model_graph,graph_subcomponent_nodes
from .model_node import ModelNode

class Model():
    nodes: Dict[str,Callable]
    nodes_graph: nx.DiGraph
    nodes_with_forced_nodes: Dict[str,Dict]
    graph: nx.DiGraph
    inputs: List[str]
    call_order: List[str]
    model_nodes: Dict
    auxiliary_nodes:List[str]

    def __init__(self,nodes:Dict[str,Callable]):
        self.nodes = nodes
        self.nodes_graph = nodes_graph(nodes)
        self.nodes_with_forced_nodes = {k:(v.forced_nodes) for k,v in self.nodes.items() if hasattr(v,"forced_nodes")}
        self.graph = model_graph(self.nodes_graph,self.nodes_with_forced_nodes)
        self.inputs = list(set(self.nodes_graph.nodes()).difference(nodes.keys()))
        self.call_order = [node for node in list(nx.topological_sort(self.graph)) if node not in self.inputs]
        self.model_nodes = {k:ModelNode(k,self.nodes,self.nodes_with_forced_nodes,self.graph) for k in self.call_order}
        self.auxiliary_nodes = list(set(self.graph.nodes()).difference(self.nodes_graph.nodes()))

    def compute(self,input:Dict,keep_auxiliary_nodes:bool=False)->Dict:
        for node_name in self.call_order:
            model_node = self.model_nodes[node_name]
            call_input = [input[k] for k in model_node.inputs]
            input[node_name] = model_node.compute(*call_input)
        if not keep_auxiliary_nodes:
            for auxiliary_node in self.auxiliary_nodes:
                del input[auxiliary_node]
        return input
    
    def submodel(self,nodes_names:List[str]):
        subcomponent_nodes_names = graph_subcomponent_nodes(self.nodes_graph,nodes_names)
        submodel_nodes = {node_name:node for node_name,node in self.nodes.items() if node_name in subcomponent_nodes_names}
        submodel = Model(submodel_nodes)
        return submodel
    



