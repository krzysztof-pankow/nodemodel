from nodemodel.model import Model

def test_model_1():
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

def test_model_2():
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

def test_model_3():
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

def test_model_4():
    def a(x):
        return x
    a.forced_nodes = {"z":5}

    nodes = {"a":a}
    inputs = {"x":1}

    m = Model(nodes)
    assert set(m.auxiliary_nodes) == set()
    assert m.compute(inputs) == {'x': 1, 'a': 1}

def test_model_5():
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
    assert m.nodes_with_forced_nodes == {'b': {'x': 5, 'y': 3}, 'c': {'y': 3, 'x': 5}}
    assert m.compute(inputs) == {'x': 1, 'y': 1, 'a': 2, 'b': 8, 'c': 8}
    assert m.compute(inputs,keep_auxiliary_nodes=True) == {'x': 1, 'y': 1, 'a': 2, 'b': 8, 'c': 8, 
                                                        ('x', 5): 5, ('y', 3): 3, ('a', 'x', 5, 'y', 3): 8}
    

def test_model_6():
    def a(x):
        return x
    a.forced_nodes = {"a":5}

    m = Model({"a":a})
    assert m.compute({"x":1}) == {"x":1,"a":1}