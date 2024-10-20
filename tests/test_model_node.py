import nodemodel.model_node as md
import networkx as nx
from nodemodel.node_factory import node_factory

def test_model_node_simple():
    def a(x,y):
        pass
    node_name = "a"
    nodes = node_factory({"a":a})
    graph = nx.DiGraph()
    graph.add_edges_from([("x","a"),("y","a")])
    model_node = md.model_node_factory(node_name,nodes,graph)
    
    assert model_node.compute == a
    assert model_node.inputs == {'x': 'x', 'y': 'y'}

def test_model_node_with_forced_nodes():
    def a(x,y):
        pass
    a.forced_nodes = {"x":1,"y":2}
    node_name = "a"
    nodes = node_factory({"a":a})
    graph = nx.DiGraph()
    graph.add_edges_from([(("x",1),"a"),(("y",2),"a")])
    model_node = md.model_node_factory(node_name,nodes,graph)

    assert isinstance(model_node,md.ModelNodeWithForcedNodes)
    assert model_node.compute == a
    assert model_node.inputs == {'x': ('x', 1), 'y': ('y', 2)}

def test_model_node_with_forced_nodes_no_arguments():
    def a():
        pass
    a.forced_nodes = {"x":1,"y":2}
    node_name = "a"
    nodes = node_factory({"a":a})
    graph = nx.DiGraph()
    graph.add_nodes_from(["a"])
    model_node = md.model_node_factory(node_name,nodes,graph)

    assert isinstance(model_node,md.ModelNodeWithForcedNodes)
    assert model_node.compute == a
    assert model_node.inputs == {}

def test_model_node_forced_to_value():
    node_name = ("x",2)
    nodes = {}
    graph = nx.DiGraph()
    model_node = md.model_node_factory(node_name,nodes,graph)

    assert isinstance(model_node,md.ModelNodeForcedToValue)
    assert model_node.compute() == 2
    assert model_node.inputs == {}

def test_model_node_forced_to_node():
    node_name = ("a",("node","y"))
    nodes = {}
    graph = nx.DiGraph()
    model_node = md.model_node_factory(node_name,nodes,graph)

    assert isinstance(model_node,md.ModelNodeForcedToNode)
    assert model_node.compute(100) == 100
    assert model_node.inputs == {'x': 'y'}

def test_model_node_auxiliary():
    def a(x,y):
        pass
    a.forced_nodes = {"x":1,"y":2}
    node_name = ("a","x",1,"y",2)
    nodes = node_factory({"a":a})
    graph = nx.DiGraph()
    graph.add_edges_from([(("x",1),("a","x",1,"y",2)),(("y",2),("a","x",1,"y",2))])
    model_node = md.model_node_factory(node_name,nodes,graph)

    assert isinstance(model_node,md.ModelNodeRecalculatedWithForcedNodes)
    assert model_node.compute == a
    assert model_node.inputs == {'x': ('x', 1), 'y': ('y', 2)}
