from nodemodel.helpers import func_args,copy_func

def test_func_args():
    def f(a,*args,**kwargs):
        return a 
    assert func_args(f) == ["a"]

a = 1
b = 2

def test_copy_func():
    def f(c):
        return a + b + c

    g = copy_func(f)
    g.__name__ = "g"
    g.__globals__["a"] = 100
    g.__globals__["b"] = 200

    assert f.__name__ == "f"
    assert f.__globals__["a"] == 1
    assert f.__globals__["b"] == 2
    assert f(0.1) == 3.1

    assert g.__name__ == "g"
    assert g.__globals__["a"] == 100
    assert g.__globals__["b"] == 200
    assert g(0.1) == 300.1


#free_vars = f.__code__.co_freevars  # This gives the names of free variables

#test.__code__.co_names #Get variable names in code