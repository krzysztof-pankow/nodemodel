from typing import List,Dict,Callable,Union
from collections.abc import Hashable
from .helpers import import_modules_from_dir,flatten_dict_with_condition


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
        return f
    else:
        return decorator


def load_nodes(module_dir: str) -> Dict[str, Callable]:
    """
    Recursively imports all callable objects from a specified module directory and its submodules 
    that have a `node_tag` attribute, returning them in a dictionary.

    This function searches through all Python files in the specified directory, including 
    subdirectories, to locate callable objects that are marked with a `node_tag` attribute. 
    A callable can acquire the `node_tag` attribute either explicitly by setting it after 
    the definition or implicitly through a `@node` decorator. Additionally, the function 
    detects callables that are stored as elements within dictionaries in each module.

    Args:
        module_dir (str): The root directory path to search for modules and callables 
            with a `node_tag` attribute.

    Returns:
        Dict[str,Callable]: A dictionary where each key is the name of a callable 
        with a `node_tag` attribute, and each value is the corresponding callable 
        object imported from the specified directory and its submodules.

    Raises:
        FileNotFoundError: If the specified module directory does not exist.
        ImportError: If there is an error while importing any modules, such as 
            syntax errors or invalid paths.

    Notes:
        - This function relies on `import_modules_from_dir` to dynamically load all 
          modules from the specified directory and `flatten_dict_with_condition` to 
          filter only the callables with the `node_tag` attribute.
        - The callable objects may be regular functions, classes with a `__call__` 
          method, or callable items stored as values within dictionaries in a module.
        - If multiple callables across modules have the same name, later imports will 
          overwrite earlier ones in the dictionary.
        - Circular imports in the specified directory may cause this function to fail 
          or produce unexpected results.

    Example:
        >>> # Assuming 'my_module_dir' contains modules with callables tagged by a `@node` decorator
        >>> nodes = load_nodes('my_module_dir')
        >>> print(nodes['my_function'])  # Access a specific callable with a node_tag attribute
    """
    imported_dict = import_modules_from_dir(module_dir)
    nodes = flatten_dict_with_condition(imported_dict,lambda x: hasattr(x,"node_tag") and callable(x))
    return nodes

