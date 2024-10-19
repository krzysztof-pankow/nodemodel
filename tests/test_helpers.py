from functools import partial
from types import FunctionType

def test_f_args():
    def f(a,*args,**kwargs):
        return a
    
    assert f.__code__.co_varnames == ('a', 'args', 'kwargs')
    assert f.__code__.co_argcount == 1
    assert f.__code__.co_varnames[:f.__code__.co_argcount] == ('a',)


def test_partial_f():
    def f(a,b,c):
        return a + b + c

    g = partial(f,a = 5)
    assert not isinstance(g,FunctionType)
    assert callable(g)
    #g(1,2) #error -> multiple 'a' argument
    assert g(b=1,c=3) == 9