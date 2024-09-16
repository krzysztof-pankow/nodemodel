import networkx as nx
from typing import List,Dict,Callable

def func_args(f:Callable)->List[str]:
    return list(f.__code__.co_varnames[:f.__code__.co_argcount])

def nodes_graph(nodes:Dict[str,Callable])->nx.DiGraph:
    edges = []
    for node_name,node in nodes.items():
        deps = func_args(node)
        for dep in deps:
            edges.append((dep,node_name))
    g = nx.DiGraph()
    g.add_edges_from(edges)
    return g

def custom_tuple_concat(a, b):
    if not isinstance(a, tuple):
        a = (a,)
    if not isinstance(b, tuple):
        b = (b,)
    return a + b

def get_cond_nodes(graph:nx.DiGraph,nodes_with_forced_nodes:Dict)->List:
    ordered_nodes = list(nx.topological_sort(graph))
    cond_nodes = [node for node in ordered_nodes if node in nodes_with_forced_nodes.keys()]
    return cond_nodes


def model_graph(nodes_graph,nodes_with_forced_nodes):
    model_graph = nodes_graph.copy()
    #Sort forced nodes in nodes_with_forced_nodes -> Important to mutualize values like {"a":1,"b":2} and {"b":2,"a":1}
    nodes_with_forced_nodes = {k:dict(sorted(v.items())) for k,v in nodes_with_forced_nodes.items()}
    #Get cond_nodes -> list of of all cond nodes
    cond_nodes = get_cond_nodes(model_graph,nodes_with_forced_nodes)
    #For each node with forced nodes, do the following:
    for cond_node in cond_nodes:
        #Get cond_node_ancestors_graph -> graph of all ancestors of cond_node  + cond_node
        cond_node_ancestors = nx.ancestors(model_graph,cond_node)
        cond_node_ancestors.add(cond_node)
        cond_node_ancestors_graph = model_graph.subgraph(cond_node_ancestors).copy()#Copy subgraph to avoid some edge cases
        #Rename nodes using forced_nodes info of cond_node
        forced_nodes = nodes_with_forced_nodes[cond_node]
        for forced_node in forced_nodes.keys():
            forced_node_value = forced_nodes[forced_node]
            if forced_node in cond_node_ancestors_graph:
                forced_node_descendants = list(nx.descendants(cond_node_ancestors_graph,forced_node))
                old_names = forced_node_descendants + [forced_node]
                new_names = [custom_tuple_concat(x,(forced_node,forced_node_value)) for x in forced_node_descendants]
                new_names.append((forced_node,forced_node_value))
                name_mapping = dict(zip(old_names,new_names))
                if cond_node in name_mapping:#Do not rename cond_node
                    del name_mapping[cond_node]
                cond_node_ancestors_graph = nx.relabel_nodes(cond_node_ancestors_graph,name_mapping)
        #Remove cond_node edges with predecessors in model_graph 
        cond_node_predecessors = list(model_graph.predecessors(cond_node))
        for predecessor in cond_node_predecessors:
            model_graph.remove_edge(predecessor, cond_node)
        #Combine cond_node_ancestors_graph with initial graph
        model_graph = nx.compose(model_graph,cond_node_ancestors_graph)
    return model_graph


def graph_subcomponent_nodes(graph:nx.DiGraph,nodes_names:List)->List:
    subcomponent_nodes = set()
    for node_name in nodes_names:
        subcomponent_nodes.update(nx.ancestors(graph, node_name))
    subcomponent_nodes.update(nodes_names)
    return list(subcomponent_nodes)

