from nodemodel.graph_functions import nodes_graph
from nodemodel.graph_functions import node_ancestors_graph
from nodemodel.graph_functions import rename_forced_node_descendants
from nodemodel.graph_functions import model_graph
import networkx as nx

def test_nodes_graph():
    def b(a,x):
        pass
    def a(y):
        pass
    def c():
        pass

    g = nodes_graph(nodes={"a":a,"b":b,"c":c})
    assert set(g.edges()) == {('y', 'a'), ('x', 'b'), ('a', 'b')}
    assert set(g.nodes()) == {'a', 'x', 'b', 'y','c'}

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

def test_model_graph():
    g = nx.DiGraph()
    g.add_edges_from([("a","b"),("b","c"),("c","d"),("e","d")])
    def a():
        pass
    def b(a):
        pass
    def c(b):
        pass
    def d(e):
        pass
    d.forced_nodes = {"a":1}

    h = model_graph(nodes_graph=g,nodes={"a":a,"b":b,"c":c,"d":d})
    assert set(h.edges()) == {(('a', 1), ('b', 'a', 1)),
                            (('b', 'a', 1), ('c', 'a', 1)),
                            (('c', 'a', 1), 'd'),
                            ('a', 'b'),
                            ('b', 'c'),
                            ('e', 'd')
                            }
    assert set(h.nodes()) == {"a","b","c","d","e",("a",1),("b","a",1),("c","a",1)}