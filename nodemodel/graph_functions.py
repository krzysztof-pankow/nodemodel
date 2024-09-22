import networkx as nx
from typing import List,Dict,Callable,Union
from .helpers import func_args,custom_tuple_concat

def nodes_graph(nodes:Dict[str,Callable])->nx.DiGraph:
    edges = []
    for node_name,node in nodes.items():
        deps = func_args(node)
        for dep in deps:
            edges.append((dep,node_name))
    g = nx.DiGraph()
    g.add_edges_from(edges)
    g.add_nodes_from(list(nodes.keys()))
    return g


def model_graph(nodes_graph:nx.DiGraph,nodes_with_forced_nodes:Dict)->nx.DiGraph:
    graph = nodes_graph.copy()
    #Sort nodes_with_forced_nodes items-> Important to mutualize forced values like {"a":1,"b":2} and {"b":2,"a":1}
    nodes_with_forced_nodes = {k:dict(sorted(v.items())) for k,v in nodes_with_forced_nodes.items()}  
    ordered_nodes = list(nx.topological_sort(nodes_graph))
    cond_nodes = [node for node in ordered_nodes if node in nodes_with_forced_nodes.keys()]
    for cond_node in cond_nodes:
        #Get graph of all ancestors of cond_node in graph + cond_node
        cond_node_ancestors_graph = node_ancestors_graph(graph,cond_node)
        #Rename nodes using forced_nodes info of cond_node
        forced_nodes = nodes_with_forced_nodes[cond_node]
        for forced_node,forced_node_value in forced_nodes.items():
            if forced_node in cond_node_ancestors_graph:
                cond_node_ancestors_graph = rename_forced_node_descendants(cond_node_ancestors_graph,
                                                                           forced_node,forced_node_value,cond_node)
        #Remove cond_node edges with predecessors in the main graph 
        cond_node_predecessors = list(graph.predecessors(cond_node))
        for predecessor in cond_node_predecessors:
            graph.remove_edge(predecessor, cond_node)
        #Combine cond_node_ancestors_graph with the main graph
        graph = nx.compose(graph,cond_node_ancestors_graph)
    return graph

def node_ancestors_graph(graph:nx.DiGraph,node:str)->nx.DiGraph:
    node_ancestors = nx.ancestors(graph,node)
    node_ancestors.add(node)
    return graph.subgraph(node_ancestors).copy()

def rename_forced_node_descendants(graph:nx.DiGraph,forced_node:str,forced_node_value:Dict,
                                   skip_nodes:Union[str,List[str]])->nx.DiGraph:
    skip_nodes = [skip_nodes] if isinstance(skip_nodes, str) else skip_nodes
    forced_node_descendants = list(nx.descendants(graph,forced_node))
    forced_node_descendants_new = [custom_tuple_concat(k,(forced_node,forced_node_value)) for k in forced_node_descendants]
    name_mapping = dict(zip(forced_node_descendants,forced_node_descendants_new))
    name_mapping[forced_node] = (forced_node,forced_node_value)
    name_mapping = {k:v for k,v in name_mapping.items() if k not in skip_nodes}
    return nx.relabel_nodes(graph,name_mapping)


def graph_subcomponent_nodes(graph:nx.DiGraph,nodes_names:Union[str,List[str]])->List:
    nodes_names = [nodes_names] if isinstance(nodes_names, str) else nodes_names
    subcomponent_nodes = set()
    for node_name in nodes_names:
        subcomponent_nodes.update(nx.ancestors(graph, node_name))
    subcomponent_nodes.update(nodes_names)
    return list(subcomponent_nodes)

def check_acyclicity(graph:nx.DiGraph)->None:
    if nx.is_directed_acyclic_graph(graph):
        pass
    else:
        cycles = nx.simple_cycles(graph)
        smallest_cycle = min(cycles,key = len)
        raise ValueError(f"A cycle was detected: {smallest_cycle}")  
