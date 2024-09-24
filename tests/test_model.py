from nodemodel.model import Model
import pytest

def test_model_with_forced_nodes_and_its_properties():
    def e(b):
        return b*5

    def c(b):
        return b
    c.forced_nodes = {"y":3}

    def b(a,y):
        return a + y
    b.forced_nodes = {"x":2}

    def a(x):
        return x

    nodes = {"a":a,"b":b,"c":c,"e":e}
    input = {"x":1,"y":1}

    m = Model(nodes)
    assert set(m.nodes_graph.edges()) == {('b', 'c'), ('a', 'b'), ('x', 'a'), ('b', 'e'), ('y', 'b')}
    assert set(m.graph.edges()) == {(('y', 3), ('b', 'y', 3)), 
                                    (('a', 'x', 2), ('b', 'y', 3)), 
                                    (('b', 'y', 3), 'c'), ('x', 'a'), 
                                    (('a', 'x', 2), 'b'), 
                                    (('x', 2), ('a', 'x', 2)), 
                                    ('b', 'e'), 
                                    ('y', 'b')}
    assert m.call_order == [('x', 2), ('y', 3), 'a', ('a', 'x', 2), 'b', ('b', 'y', 3), 'e', 'c']
    assert m.model_nodes[('x', 2)].compute() == 2
    assert m.model_nodes['b'].inputs == [('a', 'x', 2), 'y']
    assert m.model_nodes['c'].inputs == [('b', 'y', 3)]
    assert set(m.auxiliary_nodes) == {('b', 'y', 3), ('a', 'x', 2), ('x', 2), ('y', 3)}
    assert m.compute(input) == {'x': 1, 'y': 1, 'a': 1, 'b': 3, 'e': 15, 'c': 5}
    assert m.compute(input,keep_auxiliary_nodes=True) == {'x': 1, 'y': 1, ('x', 2): 2, ('y', 3): 3, 'a': 1, ('a', 'x', 2): 2, 
                                'b': 3, ('b', 'y', 3): 5, 'e': 15, 'c': 5}

def test_forced_nodes_to_nodes():
    def a():
        return 1
    def b(a):
        return a
    def c(b):
        return b
    def d(c):
        return c
    d.forced_nodes = {"a":("node","e")}
    m = Model({"a":a,"b":b,"c":c,"d":d})
    assert m.compute({"e":5}) == {'e': 5, 'a': 1, 'b': 1, 'c': 1, 'd': 5}

def test_forced_nodes_with_different_values():
    def c(a):
        return a
    c.forced_nodes = {"x":7}

    def b(a):
        return a
    b.forced_nodes = {"x":5}

    def a(x):
        return x
    nodes = {"a":a,"b":b,"c":c}
    inputs = {"x":1}

    m = Model(nodes)
    assert set(m.graph.edges()) == {('x', 'a'), 
                            (('x', 5), ('a', 'x', 5)), 
                            (('a', 'x', 7), 'c'),
                            (('x', 7), ('a', 'x', 7)), 
                            (('a', 'x', 5), 'b')}
    assert set(m.auxiliary_nodes) == {('x', 5), ('a', 'x', 7), ('x', 7), ('a', 'x', 5)}
    assert m.compute(inputs) == {'x': 1, 'a': 1, 'b': 5, 'c': 7}

def test_forced_nodes_to_nodes_with_different_values():
    def c(a):
        return a
    c.forced_nodes = {"x":("node","z")}

    def b(a):
        return a
    b.forced_nodes = {"x":("node","y")}

    def a(x):
        return x
    nodes = {"a":a,"b":b,"c":c}
    inputs = {"x":1,"y":2,"z":3}

    m = Model(nodes)
    assert m.compute(inputs) == {'x': 1, 'y': 2, 'z': 3, 'a': 1, 'b': 2, 'c': 3}

def test_simple_mutualization_of_forced_nodes():
    def c(a):
        return a
    c.forced_nodes = {"x":5}

    def b(a):
        return a
    b.forced_nodes = {"x":5}

    def a(x):
        return x
    nodes = {"a":a,"b":b,"c":c}
    inputs = {"x":1}

    m = Model(nodes)
    assert set(m.auxiliary_nodes) == {('x', 5), ('a', 'x', 5)}
    assert m.compute(inputs) == {'x': 1, 'a': 1, 'b': 5, 'c': 5}

def test_simple_mutualization_of_forced_nodes_to_nodes():
    def c(a):
        return a
    c.forced_nodes = {"x":("node","y")}

    def b(a):
        return a
    b.forced_nodes = {"x":("node","y")}

    def a(x):
        return x
    nodes = {"a":a,"b":b,"c":c}
    inputs = {"x":1,"y":2}

    m = Model(nodes)
    assert set(m.auxiliary_nodes) == {('x', ('node', 'y')), ('a', 'x', ('node', 'y'))}
    assert m.compute(inputs) == {'x': 1, 'y': 2, 'a': 1, 'b': 2, 'c': 2}

def test_irrelevent_forced_nodes():
    def a(x):
        return x
    a.forced_nodes = {"z":5}
    def b(x):
        return x
    b.forced_nodes = {"z":("node","a")}

    nodes = {"a":a,"b":b}
    inputs = {"x":1}

    m = Model(nodes)
    assert set(m.auxiliary_nodes) == set()
    assert m.compute(inputs) == {'x': 1, 'a': 1, 'b':1}
    
def test_mutualization_of_forced_nodes():
    def b(a):
        return a
    b.forced_nodes = {"x":5,"y":3}

    def c(a):
        return a
    c.forced_nodes = {"y":3,"x":5}

    def a(x,y):
        return x + y
    nodes = {"a":a,"b":b,"c":c}
    inputs = {"x":1,"y":1}

    m = Model(nodes)
    assert set(m.auxiliary_nodes) == {('y', 3), ('x', 5), ('a', 'x', 5, 'y', 3)}
    assert m.compute(inputs) == {'x': 1, 'y': 1, 'a': 2, 'b': 8, 'c': 8}
    assert m.compute(inputs,keep_auxiliary_nodes=True) == {'x': 1, 'y': 1, 'a': 2, 'b': 8, 'c': 8, 
                                                        ('x', 5): 5, ('y', 3): 3, ('a', 'x', 5, 'y', 3): 8}
    
def test_mutualization_of_forced_nodes_to_nodes():
    def b(a):
        return a
    b.forced_nodes = {"x":("node","k"),"y":("node","l")}

    def c(a):
        return a
    c.forced_nodes = {"y":("node","l"),"x":("node","k")}

    def a(x,y):
        return x + y
    nodes = {"a":a,"b":b,"c":c}
    inputs = {"x":1,"y":1,"k":2,"l":3}

    m = Model(nodes)
    assert set(m.auxiliary_nodes) == {('a', 'x', ('node', 'k'), 'y', ('node', 'l')), 
                                      ('x', ('node', 'k')), 
                                      ('y', ('node', 'l'))}
    assert m.compute(inputs) == {'x': 1, 'y': 1, 'k': 2, 'l': 3, 'a': 2, 'b': 5, 'c': 5}

def test_forced_node_which_forces_itself_to_value():
    def a(x):
        return x
    a.forced_nodes = {"a":5}

    m = Model({"a":a})
    #No effect on 'a', forced_nodes works only on ancestors on "a":
    assert m.compute({"x":1}) == {"x":1,"a":1}

def test_forced_node_which_forces_itself_to_itself():
    def a(x):
        return x
    a.forced_nodes = {"a":{"node","a"}}

    m = Model({"a":a})
    assert m.compute({"x":1}) == {"x":1,"a":1}

def test_model_with_isolated_node():
    def a():
        return 1

    m = Model({"a":a})
    assert list(m.graph.nodes()) == ['a']
    assert m.compute({}) == {'a':1}

def test_model_with_cycles_error():
    def a(b):
        return b

    def b(a):
        return a
    
    with pytest.raises(Exception) as value_exception:
        m = Model({"a":a,"b":b})
    assert (str(value_exception.value) == "A cycle was detected: ['a', 'b']" or
            str(value_exception.value) == "A cycle was detected: ['b', 'a']")
    
def test_model_with_cycles_error_from_forced_nodes_to_nodes():
    def a(x):
        return x
    a.forced_nodes = {"x":("node","b")}

    def b(a):
        return a
    
    with pytest.raises(Exception) as value_exception:
        m = Model({"a":a,"b":b})
    assert (str(value_exception.value) == "A cycle was detected: ['a', 'b']" or
            str(value_exception.value) == "A cycle was detected: ['b', 'a']")


def test_compute_with_kwargs():
    def a(x):
        return x
    
    m = Model({"a":a})
    assert m.compute({},x=1) == {"a":1}

def test_forced_node_to_ancestor_node():
    def c(b):
        return b
    def b(a,x):
        return a + x
    def a(y):
        return y
    c.forced_nodes = {"b":("node","a")}
    m = Model({"a":a,"b":b,"c":c})

    assert set(m.graph.edges()) == {('y', 'a'), ('a', 'b'), ('x', 'b'),
    ('a', ('b', ('node', 'a'))),
    ('a', 'c'),
    (('b', ('node', 'a')), 'c')
    }
    assert m.compute({"x":1,"y":1}) == {'x': 1, 'y': 1, 'a': 1, 'b': 2, 'c': 1}
    assert m.auxiliary_nodes == [('b', ('node', 'a'))]

def test_forced_node_to_descendant_node():
    #At first a bit strange that it doesn't create a cycle in the graph but it is normal:
    #Nodes are renamed and there are two b's: 'b' and ('b', 'a', ('node', 'b')))
    def c(b):
        return b
    def b(a,x):
        return a + x
    def a(y):
        return y
    c.forced_nodes = {"a":("node","b")}
    m = Model({"a":a,"b":b,"c":c})

    assert set(m.graph.edges()) == {('y', 'a'), ('x', 'b'), ('a', 'b'),
    ('b', ('a', ('node', 'b'))),
    (('a', ('node', 'b')), ('b', 'a', ('node', 'b'))), 
    ('x', ('b', 'a', ('node', 'b'))),
    (('b', 'a', ('node', 'b')), 'c')
    }
    assert m.compute({"x":1,"y":1}) == {'x': 1, 'y': 1, 'a': 1, 'b': 2, 'c': 3}
    assert set(m.auxiliary_nodes) == {('a', ('node', 'b')),('b', 'a', ('node', 'b'))}

#Check if dynamic optimisation can work

def test_forced_node_to_ancestor_and_predecessor_node():
    #node 'a' is both ancestor and predecessor of c
    def c(b,a):
        return b + a
    def b(a,x):
        return a + x
    def a(y):
        return y
    c.forced_nodes = {"b":("node","a")}
    m = Model({"a":a,"b":b,"c":c})

    assert m.compute({"x":1,"y":1}) == {'x': 1, 'y': 1, 'a': 1, 'b': 2, 'c': 2}