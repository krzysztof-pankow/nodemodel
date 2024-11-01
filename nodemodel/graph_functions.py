import networkx as nx
from typing import List,Dict,Union
from collections.abc import Hashable
from .helpers import custom_tuple_concat
from .node import Node


def nodes_graph(nodes:Dict[str,Node])->nx.DiGraph:
    """
    Constructs a directed acyclic graph (DAG) representing the relationships between node functions and their dependencies.

    The function creates a graph where each node represents a function from the input dictionary, and directed edges
    represent dependencies between these functions. A dependency exists from node A to node B if the output of node A
    is required as an input to node B.

    Additionally, if a function has the `forced_nodes` attribute, extra edges are added based on the values in 
    `forced_nodes`. Specifically, if an entry in `forced_nodes` is a tuple of the form ("node", "another_node"), 
    an edge is added from `another_node` to the function's node.

    Args:
        nodes (Dict[str, Node]): 
            A dictionary where keys are the names of the nodes (functions), and values are the functions themselves. 
            Functions may have dependencies on other nodes, based on their input arguments.
    
    Returns:
        nx.DiGraph: 
            A directed acyclic graph (DAG) where the nodes are function names and the edges represent 
            input-output relationships between functions.
    
    Raises:
        ValueError: 
            If the graph is found to have cycles (i.e., if the dependencies between nodes create a cycle).
    """

    edges = []
    for node_name,node in nodes.items():
        deps = node.inputs.values()
        for dep in deps:
            edges.append((dep,node_name))
        if hasattr(node.compute,"forced_nodes"):
            for forced_node,forced_node_value in node.compute.forced_nodes.items():
                #Add an edge ("another_node",node_name) if forced_node_value = ("node","another_node"):
                if isinstance(forced_node_value,tuple) and len(forced_node_value) == 2 and forced_node_value[0] == "node":
                    edges.append((forced_node_value[1],node_name))
    g = nx.DiGraph()
    g.add_edges_from(edges)
    g.add_nodes_from(list(nodes.keys()))
    check_acyclicity(g)
    return g


def model_graph(nodes_graph:nx.DiGraph,nodes:Dict[str,Node])->nx.DiGraph:
    """
    Constructs an extended directed acyclic graph (DAG) to handle conditional functions with 'forced_nodes' attributes.

    This function takes a base graph of node functions and modifies it to account for conditional functions, i.e., 
    functions that have the `forced_nodes` attribute. For each conditional function, its ancestors are examined, and 
    some are copied and renamed if they are also successors of the forced nodes. The result is a more detailed graph that can 
    manage these conditional relationships between functions.

    Args:
        nodes_graph (nx.DiGraph): 
            The base directed acyclic graph (DAG) representing dependencies between functions.
        nodes (Dict[str, Node]): 
            A dictionary where keys are function names and values are the functions themselves. Functions with the 
            'forced_nodes' attribute will trigger additional processing.

    Returns:
        nx.DiGraph: 
            An extended DAG where nodes and edges have been modified to reflect the conditional relationships 
            between functions, especially for those with the `forced_nodes` attribute.
    """

    #Get list of nodes which have an attribute 'forced_nodes' -> cond_nodes
    graph = nodes_graph.copy()
    ordered_nodes_names = list(nx.topological_sort(nodes_graph))
    cond_nodes = [k for k in ordered_nodes_names if k in nodes.keys() and hasattr(nodes[k].compute,"forced_nodes")]
    #Modify the main graph:
    for cond_node in cond_nodes:
        #Get graph of all ancestors of cond_node in graph + cond_node
        cond_node_ancestors_graph = node_ancestors_graph(graph,cond_node)
        #Sort to mutualize forced values like {"a":1,"b":2} and {"b":2,"a":1}
        forced_nodes = nodes[cond_node].compute.forced_nodes
        forced_nodes = dict(sorted(forced_nodes.items()))
        #Modify cond_node_ancestors_graph:
        for forced_node,forced_node_value in forced_nodes.items():
            if forced_node in cond_node_ancestors_graph and forced_node != cond_node:
                #Remove predecessors edges of forced_node
                cond_node_ancestors_graph = remove_predecessors_edges(cond_node_ancestors_graph,forced_node)
                #Rename nodes using forced_nodes info of cond_node
                cond_node_ancestors_graph = rename_forced_node_descendants(cond_node_ancestors_graph,forced_node,forced_node_value,cond_node)
                #If forced_node_value is another node, add an edge between this node and forced_node
                if isinstance(forced_node_value,tuple) and len(forced_node_value) == 2 and forced_node_value[0] == "node":
                    graph.add_edge(forced_node_value[1],(forced_node,forced_node_value))
        #Remove predecessors edges of cond_node
        graph = remove_predecessors_edges(graph,cond_node)
        #Combine cond_node_ancestors_graph with the main graph
        graph = nx.compose(graph,cond_node_ancestors_graph)
    return graph

def remove_predecessors_edges(graph:nx.DiGraph,node:str)->nx.DiGraph:
    """Removes all edges from the predecessors of a given node to the node itself."""
    cond_node_predecessors = list(graph.predecessors(node))
    for predecessor in cond_node_predecessors:
        graph.remove_edge(predecessor, node)
    return graph

def node_ancestors_graph(graph:nx.DiGraph,node:str)->nx.DiGraph:
    """Extracts a subgraph containing a node and all its ancestors from the main graph."""
    node_ancestors = nx.ancestors(graph,node)
    node_ancestors.add(node)
    return graph.subgraph(node_ancestors).copy()

def rename_forced_node_descendants(graph:nx.DiGraph,forced_node:str,forced_node_value:Hashable,
                                   skip_nodes:Union[str,List[str]])->nx.DiGraph:
    """
    Renames the descendants of a given forced node based on the forced node's value.

    This function identifies all descendants of the specified forced node in the graph and renames them using the 
    `custom_tuple_concat` function, which appends the forced node and its value to each descendant's name. 
    The forced node itself is also renamed. If any nodes are specified in `skip_nodes`, they are not renamed.
    """
    skip_nodes = [skip_nodes] if isinstance(skip_nodes, str) else skip_nodes
    forced_node_descendants = list(nx.descendants(graph,forced_node))
    forced_node_descendants_new = [custom_tuple_concat(k,(forced_node,forced_node_value)) for k in forced_node_descendants]
    name_mapping = dict(zip(forced_node_descendants,forced_node_descendants_new))
    name_mapping[forced_node] = (forced_node,forced_node_value)
    name_mapping = {k:v for k,v in name_mapping.items() if k not in skip_nodes}
    return nx.relabel_nodes(graph,name_mapping)


def graph_subcomponent_nodes(graph:nx.DiGraph,nodes_names:Union[str,List[str]])->List[str]:
    """Retrieves a list of nodes consisting of the specified nodes and all their ancestors in the graph."""
    nodes_names = [nodes_names] if isinstance(nodes_names, str) else nodes_names
    subcomponent_nodes = set()
    for node_name in nodes_names:
        subcomponent_nodes.update(nx.ancestors(graph, node_name))
    subcomponent_nodes.update(nodes_names)
    return list(subcomponent_nodes)

def check_acyclicity(graph:nx.DiGraph)->None:
    '''
    This function checks whether the given directed graph is a Directed Acyclic Graph (DAG). If the graph contains a 
    cycle, it identifies the smallest cycle and raises a `ValueError` with details about the cycle.
    '''
    if nx.is_directed_acyclic_graph(graph):
        pass
    else:
        cycles = nx.simple_cycles(graph)
        smallest_cycle = min(cycles,key = len)
        raise ValueError(f"A cycle was detected: {smallest_cycle}")
