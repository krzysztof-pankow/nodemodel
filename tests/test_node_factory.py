from nodemodel.node_factory import Node,node_factory

def test_node_class():
    def a(b,c,d = 1,*args,**kwargs):
        return 1
    node = Node(a)

    assert node.compute == a
    assert node.inputs == ['b', 'c', 'd']

def test_node_factory():
    def a(x):
        return b

    def b(y):
        return y

    b.forced_nodes = {"a":5}
    nodes = node_factory({"a":a,"b":b})

    assert nodes["a"].compute == a
    assert nodes["a"].inputs == ["x"]
    assert not hasattr(nodes["a"],"forced_nodes")
    assert nodes["b"].compute == b
    assert nodes["b"].inputs == ["y"]
    assert hasattr(nodes["b"],"forced_nodes")
