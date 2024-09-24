from typing import List,Callable

def func_args(f:Callable)->List[str]:
    return list(f.__code__.co_varnames[:f.__code__.co_argcount])

def custom_tuple_concat(a, b):
    if not isinstance(a, tuple):
        a = (a,)
    if not isinstance(b, tuple):
        b = (b,)
    return a + b