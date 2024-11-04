from nodemodel.helpers import func_args,callable_args,flatten_dict_with_condition


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


def test_flatten_dict_with_condition():
    test = {"a": {"b": 1, "c": 2, "o": {"m": "l"}, "x": 7}}

    assert flatten_dict_with_condition(test,lambda x: type(x) == int) == {'b': 1, 'c': 2, 'x': 7}
    assert flatten_dict_with_condition(test,lambda x: type(x) == str) == {'m':"l"}
    assert flatten_dict_with_condition(test,lambda x: False) == {}