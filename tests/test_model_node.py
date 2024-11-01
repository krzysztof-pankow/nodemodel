from nodemodel.node import Node,NodeWithForcedNodes,NodeForcedToValue,NodeForcedToNode,node_factory
from nodemodel.helpers import call_inputs
import networkx as nx


def test_model_node_simple():
    def a(x,y):
        pass
    node_name = "a"
    nodes = {"a":Node(a)}
    graph = nx.DiGraph()
    graph.add_edges_from([("x","a"),("y","a")])
    model_node = node_factory(node_name,nodes,graph)
    
    assert model_node.compute == a
    assert model_node.inputs == {'x': 'x', 'y': 'y'}

def test_model_node_with_forced_nodes():
    def a(x,y):
        pass
    a.forced_nodes = {"x":1,"y":2}
    node_name = "a"
    nodes = {"a":Node(a)}
    graph = nx.DiGraph()
    graph.add_edges_from([(("x",1),"a"),(("y",2),"a")])
    model_node = node_factory(node_name,nodes,graph)

    assert isinstance(model_node,NodeWithForcedNodes)
    assert model_node.compute == a
    assert model_node.inputs == {'x': ('x', 1), 'y': ('y', 2)}

def test_model_node_with_forced_nodes_no_arguments():
    def a():
        pass
    a.forced_nodes = {"x":1,"y":2}
    node_name = "a"
    nodes = {"a":Node(a)}
    graph = nx.DiGraph()
    graph.add_nodes_from(["a"])
    model_node = node_factory(node_name,nodes,graph)

    assert isinstance(model_node,NodeWithForcedNodes)
    assert model_node.compute == a
    assert model_node.inputs == {}

def test_model_node_forced_to_value():
    node_name = ("x",2)
    nodes = {}
    graph = nx.DiGraph()
    model_node = node_factory(node_name,nodes,graph)

    assert isinstance(model_node,NodeForcedToValue)
    assert model_node.compute() == 2
    assert model_node.inputs == {}

def test_model_node_forced_to_node():
    node_name = ("a",("node","y"))
    nodes = {}
    graph = nx.DiGraph()
    model_node = node_factory(node_name,nodes,graph)

    assert isinstance(model_node,NodeForcedToNode)
    assert model_node.compute(100) == 100
    assert model_node.inputs == {'x': 'y'}

def test_model_node_auxiliary():
    def a(x,y):
        pass
    a.forced_nodes = {"x":1,"y":2}
    node_name = ("a","x",1,"y",2)
    nodes = {"a":Node(a)}
    graph = nx.DiGraph()
    graph.add_edges_from([(("x",1),("a","x",1,"y",2)),(("y",2),("a","x",1,"y",2))])
    model_node = node_factory(node_name,nodes,graph)

    assert isinstance(model_node,NodeWithForcedNodes)
    assert model_node.compute == a
    assert model_node.inputs == {'x': ('x', 1), 'y': ('y', 2)}

def test_callable_nodes():
    class A():
        def __init__(self,k,q):
            self.inputs = {"b":f"b_{k}"}
            self.forced_nodes = {"h":k}
            self.q = q

        def __call__(self,b,c):
            return (b + c)*self.q
    
    nodes = {"a_x":Node(A("x",1)),"a_y":Node(A("y",10)),"a_z":Node(A("z",100))}
    input = {'c':0,'b_x':1,'b_y':2,'b_z':3}
    
    assert nodes['a_x'].inputs == {'b': 'b_x', 'c': 'c'}
    assert nodes['a_y'].inputs == {'b': 'b_y', 'c': 'c'}
    assert nodes['a_z'].inputs == {'b': 'b_z', 'c': 'c'}

    assert nodes['a_x'].compute(**call_inputs(input,nodes['a_x'].inputs)) == 1
    assert nodes['a_y'].compute(**call_inputs(input,nodes['a_y'].inputs)) == 20
    assert nodes['a_z'].compute(**call_inputs(input,nodes['a_z'].inputs)) == 300

    assert nodes['a_x'].compute.forced_nodes == {'h': "x"}
    assert nodes['a_y'].compute.forced_nodes == {'h': "y"}
    assert nodes['a_z'].compute.forced_nodes == {'h': "z"}

