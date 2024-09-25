from typing import List,Callable,Union
from collections.abc import Hashable

def func_args(f:Callable)->List[str]:
    """Returns a list of the function's argument names."""
    return list(f.__code__.co_varnames[:f.__code__.co_argcount])

def custom_tuple_concat(a:Union[Hashable,tuple], b:Union[Hashable,tuple])->tuple:
    """Concatenation that ensures both values are converted to tuples."""
    if not isinstance(a, tuple):
        a = (a,)
    if not isinstance(b, tuple):
        b = (b,)
    return a + b