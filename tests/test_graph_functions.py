from nodemodel.graph_functions import nodes_graph
from nodemodel.graph_functions import node_ancestors_graph
from nodemodel.graph_functions import rename_forced_node_descendants
from nodemodel.graph_functions import model_graph
from nodemodel.node import Node
import networkx as nx


def test_nodes_graph():
    def b(a,x):
        pass
    def a(y):
        pass
    def c():
        pass
    nodes = {"a":Node(a),"b":Node(b),"c":Node(c)}
    g = nodes_graph(nodes)

    assert set(g.edges()) == {('y', 'a'), ('x', 'b'), ('a', 'b')}
    assert set(g.nodes()) == {'a', 'x', 'b', 'y','c'}

def test_nodes_graph_with_forced_node_to_node():
    def a():
        pass
    def b(a):
        pass
    def c(b):
        pass
    c.forced_nodes = {"b":("node","a")}
    nodes = {"a":Node(a),"b":Node(b),"c":Node(c)}
    g = nodes_graph(nodes)

    assert set(g.edges()) == {('a', 'b'),('b', 'c'),('a', 'c')}

def test_node_ancestors_graph():
    g = nx.DiGraph()
    g.add_edges_from([("a","b"),("b","c"),("c","d")])
    h = node_ancestors_graph(graph=g,node="c")

    assert set(h.edges()) == {('a', 'b'), ('b', 'c')}
    assert set(h.nodes()) == {'a', 'b', 'c'}

def rename_forced_node_descendants():
    g = nx.DiGraph()
    g.add_edges_from([("a",("b","y","5")),(("b","y","5"),"c"),("c","d"),("e","d")])
    h = rename_forced_node_descendants(graph=g,forced_node="a",forced_node_value=1,skip_nodes="d")

    assert set(h.edges()) == {(('a', 1), ('b', 'y', '5', 'a', 1)),
                            (('b', 'y', '5', 'a', 1), ('c', 'a', 1)), 
                            (('c', 'a', 1), 'd'),
                            ('e', 'd')
                            }
    assert set(h.nodes()) == {('a', 1), ('b', 'y', '5', 'a', 1), ('c', 'a', 1), 'e', 'd'}

def rename_forced_node_descendants_with_forced_node_to_node():
    g = nx.DiGraph()
    g.add_edges_from([("a",("b","y","5")),(("b","y","5"),"c"),("c","d"),("e","d")])
    h = rename_forced_node_descendants(graph=g,forced_node="a",forced_node_value=("node","x"),skip_nodes="d")

    assert set(h.edges()) == {(('a', ('node', 'x')), ('b', 'y', '5', 'a', ('node', 'x'))),
                            (('b', 'y', '5', 'a', ('node', 'x')), ('c', 'a', ('node', 'x'))),
                            (('c', 'a', ('node', 'x')), 'd'),
                            ('e', 'd')
                            }
    assert set(h.nodes()) == {('a', ('node', 'x')), ('b', 'y', '5', 'a', ('node', 'x')), ('c', 'a', ('node', 'x')), 'd', 'e'}

def test_model_graph():
    def a():
        pass
    def b(a):
        pass
    def c(b):
        pass
    def d(c,e):
        pass
    d.forced_nodes = {"a":1}
    nodes = {"a":Node(a),"b":Node(b),"c":Node(c),"d":Node(d)}
    g = nodes_graph(nodes)
    h = model_graph(nodes_graph=g,nodes=nodes)

    assert set(h.edges()) == {(('a', 1), ('b', 'a', 1)),
                            (('b', 'a', 1), ('c', 'a', 1)),
                            (('c', 'a', 1), 'd'),
                            ('a', 'b'),
                            ('b', 'c'),
                            ('e', 'd')
                            }
    assert set(h.nodes()) == {"a","b","c","d","e",("a",1),("b","a",1),("c","a",1)}

def test_model_graph_with_forced_node_to_node():
    def a():
        pass
    def b(a):
        pass
    def c(b):
        pass
    def d(c):
        pass
    d.forced_nodes = {"a":("node","e")}
    nodes = {"a":Node(a),"b":Node(b),"c":Node(c),"d":Node(d)}
    g = nodes_graph(nodes)
    h = model_graph(nodes_graph=g,nodes=nodes)

    assert set(h.edges()) == {('a', 'b'), ('b', 'c'),
        ('e', ('a', ('node', 'e'))), 
        (('a', ('node', 'e')), ('b', 'a', ('node', 'e'))),
        (('b', 'a', ('node', 'e')), ('c', 'a', ('node', 'e'))), 
        (('c', 'a', ('node', 'e')), 'd'), ('e', 'd')}
    assert set(h.nodes()) == {"a","b","c","d","e",("a",('node', 'e')),("b","a",('node', 'e')),("c","a",('node', 'e'))}
    