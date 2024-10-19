from typing import List,Union,Dict
from collections.abc import Hashable
from types import FunctionType
import os
import importlib
from types import ModuleType

def func_args(f:FunctionType)->List[str]:
    """Returns a list of the function's argument names."""
    return list(f.__code__.co_varnames[:f.__code__.co_argcount])

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