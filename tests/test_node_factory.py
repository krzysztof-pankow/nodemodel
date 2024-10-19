from nodemodel.node_factory import Node,node_factory,node_generator

def test_node_class():
    def a(b,c,d = 1,*args,**kwargs):
        return 1
    node = Node(a)

    assert node.compute == a
    assert node.inputs == {'b': 'b', 'c': 'c', 'd': 'd'}

def test_node_factory():
    def a(x):
        return b

    def b(y):
        return y

    b.forced_nodes = {"a":5}
    nodes = node_factory({"a":a,"b":b})

    assert nodes["a"].compute == a
    assert nodes["a"].inputs == {'x': 'x'}
    assert not hasattr(nodes["a"],"forced_nodes")
    assert nodes["b"].compute == b
    assert nodes["b"].inputs == {'y': 'y'}
    assert hasattr(nodes["b"],"forced_nodes")

def test_node_generator():
    class A_Factory():
        def __init__(self,k):
            self.a = f"a_{k}"
            self.b = f"b_{k}"
    def a(b):
        return b
    a.node_cases = [A_Factory(1),A_Factory(2),A_Factory(3)]

    nodes = node_generator("a",a)

    assert list(nodes.keys()) == ['a_1', 'a_2', 'a_3']

