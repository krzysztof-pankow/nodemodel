from typing import List,Union,Dict,Callable
from collections.abc import Hashable
from types import FunctionType,ModuleType,MethodType
import os
import importlib


def func_args(f:Union[FunctionType,MethodType])->List[str]:
    """Returns a list of the function's argument names."""
    return list(f.__code__.co_varnames[:f.__code__.co_argcount])

def callable_args(obj:Callable)->List[str]:
    """Returns a list of the callable object argument names exluding 'self' argument."""
    if isinstance(obj,FunctionType):
        return func_args(obj)
    else:
        args = func_args(obj.__call__)
        return [arg for arg in args if arg != "self"]

def call_inputs(input:Dict,node_inputs:Dict[str,str])-> Dict:
    return {k:input[v] for k,v in node_inputs.items()}

def custom_tuple_concat(a:Union[Hashable,tuple], b:Union[Hashable,tuple])->tuple:
    """Concatenation that ensures both values are converted to tuples."""
    if not isinstance(a, tuple):
        a = (a,)
    if not isinstance(b, tuple):
        b = (b,)
    return a + b

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

def flatten_dict_with_condition(d:Dict,f_cond:Callable)->Dict:
    flat_dict = {}
    for key, value in d.items():
        if isinstance(value, dict):
            flat_dict.update(flatten_dict_with_condition(value,f_cond))
        else:
            if f_cond(value):
                flat_dict[key] = value
    return flat_dict
