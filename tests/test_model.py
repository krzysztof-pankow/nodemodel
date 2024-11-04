from nodemodel.model import Model
from nodemodel.utils import node
import pytest
from typing import List


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
    assert m.model_nodes['b'].inputs == {'y': 'y', 'a': ('a', 'x', 2)}
    assert m.model_nodes['c'].inputs == {'b': ('b', 'y', 3)}
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
    assert m.model_nodes["d"].inputs == {'c': ('c', 'a', ('node', 'e'))}
    assert m.model_nodes[('c', 'a', ('node', 'e'))].inputs == {'b': ('b', 'a', ('node', 'e'))}
    assert m.model_nodes[('b', 'a', ('node', 'e'))].inputs == {'a': ('a', ('node', 'e'))}
    assert m.model_nodes[('a', ('node', 'e'))].inputs == {'x': 'e'}
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

def test_model_with_node_decorator():
    @node
    def e(b):
        return b*5
    
    @node(y = 3)
    def c(b):
        return b

    @node(x = 2)
    def b(a,y):
        return a + y

    @node
    def a(x):
        return x
    
    nodes = {"a":a,"b":b,"c":c,"e":e}
    input = {"x":1,"y":1}

    m = Model(nodes)
    assert m.compute(input) == {'x': 1, 'y': 1, 'a': 1, 'b': 3, 'e': 15, 'c': 5}

def test_model_with_callables():
    class A():
        def __init__(self,v:str,coeff:float):
            self.name = f"a_{v}"
            self.y = f"y_{v}"
            self.inputs = {"y":self.y}
            self.coeff = coeff

        def __call__(self,x,y):
            return (x * self.coeff) + y

    class B():
        def __init__(self,v:str,forced_value:float):
            self.name = f"b_{v}"
            self.a = f"a_{v}"
            self.inputs = {"a":self.a}
            self.forced_nodes = {"x":forced_value}
            
        def __call__(self,a):
            return a
    
    a_config = [{"v":"k","coeff":1},{"v":"l","coeff":2},{"v":"m","coeff":3}]
    b_config = [{"v":"k","forced_value":1},{"v":"l","forced_value":10},{"v":"m","forced_value":100}]

    nodes = {}
    for config in a_config:
        node = A(**config)
        nodes[node.name] = node
    for config in b_config:
        node = B(**config)
        nodes[node.name] = node

    m = Model(nodes)

    assert set(m.inputs) == {'y_m', 'y_k', 'y_l', 'x'}
    assert list(m.nodes.keys()) == ['a_k', 'a_l', 'a_m', 'b_k', 'b_l', 'b_m']
    assert m.nodes['b_k'].inputs == {'a': 'a_k'}
    assert m.model_nodes['b_k'].inputs == {'a': ('a_k', 'x', 1)}
    assert set(m.auxiliary_nodes) == {('x', 1),('x', 10), ('x', 100), 
                                    ('a_k', 'x', 1), ('a_l', 'x', 10), ('a_m', 'x', 100)}
    assert m.compute({"x":1000,"y_k":0.1,"y_l":0.2,"y_m":0.3}) == {'x': 1000, 'y_k': 0.1, 'y_l': 0.2, 'y_m': 0.3, 
                                                                   'a_k': 1000.1, 'a_l': 2000.2, 'a_m': 3000.3, 
                                                                   'b_k': 1.1, 'b_l': 20.2, 'b_m': 300.3}
    
def test_model_with_callables_and_varying_nb_arguments():
    class A():
        def __init__(self,v:str,coeffs:List[str]):
            self.name = f"a_{v}"
            self.y = f"y_{v}"
            self.inputs = {"y":self.y}
            for coeff in coeffs:
                self.inputs[coeff] = coeff
            
        def __call__(self,x,y,**coeffs):
            output = y
            for coeff in coeffs.values():
                output = output + coeff
            output = output * x
            return output
        
    class B():
        def __init__(self,v:str,forced_value:float):
            self.name = f"b_{v}"
            self.a = f"a_{v}"
            self.inputs = {"a":self.a}
            self.forced_nodes = {"x":forced_value}
            
        def __call__(self,a):
            return a
        

    a_config = [{"v":"k","coeffs":["q"]},{"v":"l","coeffs":["q","s"]},{"v":"m","coeffs":["q","s","d"]}]
    b_config = [{"v":"k","forced_value":1},{"v":"l","forced_value":10},{"v":"m","forced_value":100}]

    nodes = {}
    for config in a_config:
        node = A(**config)
        nodes[node.name] = node
    for config in b_config:
        node = B(**config)
        nodes[node.name] = node
    m = Model(nodes)

    assert set(m.inputs) == {'y_m', 'y_k', 'y_l', 'q','s','d','x'}
    assert list(m.nodes.keys()) == ['a_k', 'a_l', 'a_m', 'b_k', 'b_l', 'b_m']
    assert m.nodes['a_m'].inputs == {'x': 'x', 'y': 'y_m', 'q': 'q', 's': 's', 'd': 'd'}
    assert m.model_nodes['a_m'].inputs == m.nodes['a_m'].inputs
    assert m.nodes['b_k'].inputs == {'a': 'a_k'}
    assert m.model_nodes['b_k'].inputs == {'a': ('a_k', 'x', 1)}
    assert set(m.auxiliary_nodes) == {('x', 1),('x', 10), ('x', 100), 
                                    ('a_k', 'x', 1), ('a_l', 'x', 10), ('a_m', 'x', 100)}
    assert m.compute({"x":1000,"y_k":0,"y_l":10,"y_m":100,"q":1,"s":2,"d":3}) == {'x': 1000, 'y_k': 0, 'y_l': 10, 'y_m': 100, 
                                                                                  'q': 1, 's': 2, 'd': 3, 
                                    'a_k': 1000, 'a_l': 13000, 'a_m': 106000, 'b_k': 1, 'b_l': 130, 'b_m': 10600}
    