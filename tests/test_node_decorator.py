from nodemodel.utils import node
from nodemodel.model import Model

def test_node_decorator_1():
    @node
    def test():
        '''test_doc'''
        return 1

    assert test.__doc__ == "test_doc"
    assert test.__name__ == "test"
    assert test() == 1
    assert hasattr(test,"node_tag")
    assert not hasattr(test,"forced_nodes")

def test_node_decorator_2():
    @node()
    def test():
        '''test_doc'''
        return 1

    assert test.__doc__ == "test_doc"
    assert test.__name__ == "test"
    assert test() == 1
    assert hasattr(test,"node_tag")
    assert not hasattr(test,"forced_nodes")

def test_node_decorator_3():
    @node(tag = "my_tag")
    def test():
        '''test_doc'''
        return 1

    assert test.__doc__ == "test_doc"
    assert test.__name__ == "test"
    assert test() == 1
    assert hasattr(test,"node_tag")
    assert test.node_tag == "my_tag"
    assert not hasattr(test,"forced_nodes")

def test_node_decorator_4():
    @node(tag = "my_tag",a = 5,b = "c")
    def test():
        '''test_doc'''
        return 1

    assert test.__doc__ == "test_doc"
    assert test.__name__ == "test"
    assert test() == 1
    assert hasattr(test,"node_tag")
    assert test.node_tag == "my_tag"
    assert hasattr(test,"forced_nodes")
    assert test.forced_nodes == {'a':5,'b':"c"}

def test_node_decorator_with_model():
    @node
    def e(b):
        return b*5
    
    @node(y = 3)
    def c(b):
        return b

    @node(x = 2)
    def b(a,y):
        return a + y

    @node
    def a(x):
        return x
    
    nodes = {"a":a,"b":b,"c":c,"e":e}
    input = {"x":1,"y":1}

    m = Model(nodes)
    assert m.compute(input) == {'x': 1, 'y': 1, 'a': 1, 'b': 3, 'e': 15, 'c': 5}