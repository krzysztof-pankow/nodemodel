from nodemodel.node_factory import Node,node_factory,generate_nodes
from nodemodel.helpers import call_inputs

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
    assert not hasattr(nodes["a"].compute,"forced_nodes")
    assert nodes["b"].compute == b
    assert nodes["b"].inputs == {'y': 'y'}
    assert hasattr(nodes["b"].compute,"forced_nodes")

q = 0.1#needs to be outside of test function
def test_node_generator():
    class A_Factory():
        def __init__(self,k,q):
            self.a = f"a_{k}"
            self.b = f"b_{k}"
            self.q = q

    a_cases = [A_Factory("x",1),A_Factory("y",10),A_Factory("z",100)]
    
    def a(b,c):
        return (b + c)*q
    a.node_cases = a_cases

    nodes = generate_nodes("a",a)
    input = {'c':0,'b_x':1,'b_y':2,'b_z':3}
    
    assert nodes['a_x'].inputs == {'b': 'b_x', 'c': 'c'}
    assert nodes['a_y'].inputs == {'b': 'b_y', 'c': 'c'}
    assert nodes['a_z'].inputs == {'b': 'b_z', 'c': 'c'}

    assert a.__name__ == "a"
    assert nodes['a_x'].compute.__name__ == "a_x"
    assert nodes['a_y'].compute.__name__ == "a_y"
    assert nodes['a_z'].compute.__name__ == "a_z"

    assert a(b=1,c=0) == 0.1
    assert nodes['a_x'].compute(**call_inputs(input,nodes['a_x'].inputs)) == 1
    assert nodes['a_y'].compute(**call_inputs(input,nodes['a_y'].inputs)) == 20
    assert nodes['a_z'].compute(**call_inputs(input,nodes['a_z'].inputs)) == 300


def test_node_generator_with_forced_nodes():
        class A_Factory():
            def __init__(self,k,forced_nodes):
                self.a = f"a_{k}"
                self.forced_nodes = forced_nodes
        
        a_cases = [A_Factory("x",{"b":20}),A_Factory("y",{"b":30})]

        def a():
            return 1
        a.forced_nodes = {"b":10}
        a.node_cases = a_cases

        nodes = generate_nodes("a",a)

        assert a.forced_nodes == {'b':10}
        assert nodes['a_x'].compute.forced_nodes == {'b': 20}
        assert nodes['a_y'].compute.forced_nodes == {'b': 30}


