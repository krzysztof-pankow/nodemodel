import os
import importlib
from types import ModuleType
from typing import List,Dict,Callable,Union
from collections.abc import Hashable


def node(f:Callable = None,tag:Union[str,List[str]] = None,**forced_nodes:Dict[str,Hashable])->Callable:
    """
    A function decorator that adds a `node_tag` attribute to the decorated function, distinguishing it among other callables.

    The `node_tag` attribute serves as an identifier for the function. Optionally, a `forced_nodes` attribute can be added 
    to indicate that the function is conditional. Conditional functions are executed in a graph of functions after forcing 
    the results of specific other functions (nodes). These forced nodes can be set to either a hashable value or another node 
    in the function graph.

    Args:
        f (Callable, optional): The function to be decorated. Defaults to None.
        tag (Union[str, List[str]], optional): Sets the `node_tag` attribute with a string or a list of strings. 
                                               Useful for grouping nodes. Defaults to None.
        **forced_nodes: Specifies that the function is conditional by adding a `forced_nodes` attribute. The keys 
                        represent the names of the nodes to be forced, and the values indicate what these nodes 
                        are forced to.
        
        Example:
            @node(a=5, b=('node', 'c')) adds a `forced_nodes` attribute to the function as {"a": 5, "b": ('node', 'c')}.
            This means that before executing the decorated function, node "a" is forced to the value 5, and node "b" 
            is forced to the result of node "c". The ('node', 'name_of_node') convention specifies that one node is 
            forced to another node.

    Returns:
        Callable: The decorated function with the `node_tag` attribute and, optionally, the `forced_nodes` attribute.
    """
    def decorator(g):
        g.node_tag = tag
        if len(forced_nodes) > 0:
            g.forced_nodes = forced_nodes
        return g
    
    if callable(f):
        f.node_tag = tag
        if len(forced_nodes) > 0:
            f.forced_nodes = forced_nodes
        return f
    else:
        return decorator

def load_nodes(module_dir:str)-> Dict[str,Callable]:
    """
    Recursively imports all functions from a module and its submodules that have a `node_tag` attribute into a dictionary.

    Functions can have the `node_tag` attribute either by explicitly setting it after the function definition,
    or implicitly by using the `@node` decorator.

    Args:
        module_dir (str): The directory path of the root module to search for functions with a `node_tag` attribute.

    Returns:
        Dict[str, Callable]: A dictionary where the keys are the names of the functions and the values are the 
                             corresponding callable functions that have been imported from the specified module 
                             and its submodules.
    """
    imported_dict = import_modules_from_dir(module_dir)
    nodes = {k:v for k,v in imported_dict.items() if hasattr(v,"node_tag") and callable(v)}
    return nodes

def import_modules_from_dir(module_dir:str)-> Dict:
    """Imports all modules and submodules from a directory and stores them in a dictionary."""
    imported_dict = {}
    for root, dirs, files in os.walk(module_dir):
        for f in files:
            if f.endswith(".py"):
                module_path = os.path.join(root,f)
                module_name = f.split(".")[0]
                imported_module = import_module(module_name, module_path)
                imported_dict.update(imported_module.__dict__)
    return imported_dict

def import_module(module_name:str, module_path:str)-> ModuleType:
    """Imports a module in a dynamic way."""
    module_spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module