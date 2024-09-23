from nodemodel.model_node import ModelNode
import networkx as nx

def test_model_node_with_forced_values():
    def a(x,y):
        pass
    a.forced_nodes = {"x":1,"y":2}
    node_name = "a"
    nodes = {"a":a}
    graph = nx.DiGraph()
    graph.add_edges_from([(("x",1),"a"),(("y",2),"a")])

    model_node = ModelNode(node_name,nodes,graph)
    assert model_node.compute == a
    assert model_node.inputs == [("x",1),("y",2)]

def test_model_node_with_forced_values_no_arguments():
    def a():
        pass
    a.forced_nodes = {"x":1,"y":2}
    node_name = "a"
    nodes = {"a":a}
    graph = nx.DiGraph()
    graph.add_nodes_from(["a"])
    model_node = ModelNode(node_name,nodes,graph)

    assert model_node.compute == a
    assert model_node.inputs == []

def test_model_node_simple():
    def a(x,y):
        pass
    node_name = "a"
    nodes = {"a":a}
    graph = nx.DiGraph()
    graph.add_edges_from([("x","a"),("y","a")])
    model_node = ModelNode(node_name,nodes,graph)

    assert model_node.compute == a
    assert model_node.inputs == ["x","y"]


def test_model_node_forced_value():
    node_name = ("x",2)
    nodes = {}
    graph = nx.DiGraph()
    model_node = ModelNode(node_name,nodes,graph)

    assert model_node.compute() == 2
    assert model_node.inputs == []

def test_model_node_auxiliary():
    def a(x,y):
        pass
    a.forced_nodes = {"x":1,"y":2}
    node_name = ("a","x",1,"y",2)
    nodes = {"a":a}
    graph = nx.DiGraph()
    graph.add_edges_from([(("x",1),("a","x",1,"y",2)),(("y",2),("a","x",1,"y",2))])

    model_node = ModelNode(node_name,nodes,graph)
    assert model_node.compute == a
    assert model_node.inputs == [("x",1),("y",2)]


