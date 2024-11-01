from nodemodel.helpers import func_args,callable_args


def test_func_args():
    def f(a,*args,**kwargs):
        return a
    assert func_args(f) == ["a"]

def test_callable_args():
    def f(a,*args,**kwargs):
        return a
    class F_Class():
        def __call__(self,a,b,*args,**kwargs):
            return a + b
    f_object = F_Class()
    
    assert callable_args(f) == ["a"]
    assert callable_args(f_object) == ["a","b"]
