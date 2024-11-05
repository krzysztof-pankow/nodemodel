from typing import List,Union,Dict,Callable
from collections.abc import Hashable
from types import FunctionType,ModuleType,MethodType
import os
import importlib


def func_args(f: Union[FunctionType, MethodType]) -> List[str]:
    """
    Returns a list of the function's argument names.
    """
    return list(f.__code__.co_varnames[:f.__code__.co_argcount])

def callable_args(obj: Callable) -> List[str]:
    """
    Returns a list of the callable object's argument names excluding 'self'.
    """
    if isinstance(obj,FunctionType):
        return func_args(obj)
    else:
        args = func_args(obj.__call__)
        return [arg for arg in args if arg != "self"]

def call_inputs(input: Dict, node_inputs: Dict[str, str]) -> Dict:
    """
    Calls and retrieves input values based on specified node inputs.
    """
    return {k:input[v] for k,v in node_inputs.items()}

def custom_tuple_concat(a:Union[Hashable,tuple], b:Union[Hashable,tuple])->tuple:
    """
    Concatenates two values, ensuring that both are converted to tuples.
    """

    if not isinstance(a, tuple):
        a = (a,)
    if not isinstance(b, tuple):
        b = (b,)
    return a + b

def import_modules_from_dir(module_dir: str) -> Dict:
    """
    Imports all Python modules from a specified directory, including 
    submodules in nested directories, and returns a dictionary of 
    their combined attributes and functions.

    This function traverses a given directory to find all Python files, 
    dynamically importing each as a module and collecting all accessible 
    attributes, functions, and classes into a single dictionary. This is 
    useful for scenarios where you want to aggregate the functionality 
    of multiple modules from a directory into one namespace.

    Args:
        module_dir (str): The path to the directory containing the modules 
            and submodules to import. The function will recursively search 
            this directory for all .py files.

    Returns:
        Dict: A dictionary containing all the imported attributes, functions, 
        and classes from the modules in `module_dir`. The dictionary keys 
        are attribute names, and the values are the corresponding objects 
        from the imported modules.

    Raises:
        FileNotFoundError: If the specified directory does not exist.
        ImportError: If there is an error importing any of the modules, 
            such as syntax errors or invalid paths.

    Notes:
        - This function imports modules dynamically, so it may not detect 
          circular dependencies within the directory structure.
        - If multiple modules contain attributes with the same names, 
          later imports will overwrite earlier ones in the dictionary.

    Example:
        >>> # Assuming 'my_directory' contains module files a.py, b.py, and c.py
        >>> imported_content = import_modules_from_dir('my_directory')
        >>> print(imported_content['some_function'])  # Access a function from one of the modules
    """
    imported_dict = {}
    for root, dirs, files in os.walk(module_dir):
        for f in files:
            if f.endswith(".py"):
                module_path = os.path.join(root,f)
                module_name = f.split(".")[0]
                imported_module = import_module(module_name, module_path)
                imported_dict.update(imported_module.__dict__)
    return imported_dict

def import_module(module_name: str, module_path: str) -> ModuleType:
    """
    Dynamically imports a module from a specified file path.

    This function loads and imports a Python module from a given file path
    at runtime, allowing for dynamic module loading even if the module is not
    available in the standard search path. This is particularly useful for 
    loading modules stored in custom or non-standard locations.

    Args:
        module_name (str): The name to assign to the module once it is imported. This name is 
            used to reference the module within the current Python runtime.
        module_path (str): The file path of the module to import. This should be the path to the 
            module's .py file.

    Returns:
        ModuleType: The imported module object, which can then be used to access 
        the module's attributes and functions.

    Raises:
        FileNotFoundError: If the specified module file does not exist at the given path.
        ImportError: If there is an error loading the module, such as syntax errors 
            within the module or invalid paths.

    Example:
        >>> # Assuming 'example_module.py' is in the same directory
        >>> module = import_module('example_module', './example_module.py')
        >>> module.some_function()
    """
    module_spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module

def flatten_dict_with_condition(d: Dict, f_cond: Callable) -> Dict:
    """
    Recursively flattens a nested dictionary, including only items that meet a specified condition.

    This function traverses a nested dictionary structure and flattens it into a single-level dictionary.
    Only key-value pairs where the value satisfies the provided conditional function `f_cond` are included
    in the output dictionary.

    Args:
        d (Dict): The dictionary to flatten. It can contain nested dictionaries as values.
        f_cond (Callable): A function that takes a dictionary value as input and returns a boolean.
            Only values that make `f_cond(value)` return True are kept in the resulting dictionary.

    Returns:
        Dict: A flattened dictionary containing only the key-value pairs that satisfy the condition
        specified by `f_cond`.

    Example:
        >>> d = {'a': 1, 'b': {'c': 2, 'd': {'e': 3}}, 'f': 'hello'}
        >>> flatten_dict_with_condition(d, lambda x: isinstance(x, int) and x > 1)
        {'c': 2, 'e': 3}
    """
    flat_dict = {}
    for key, value in d.items():
        if isinstance(value, dict):
            flat_dict.update(flatten_dict_with_condition(value,f_cond))
        else:
            if f_cond(value):
                flat_dict[key] = value
    return flat_dict
