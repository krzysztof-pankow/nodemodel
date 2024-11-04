from nodemodel.utils import load_nodes
from nodemodel.model import Model
import os

def create_folder_structure(tmp_path,node_1_code,node_2_code):
    submodule_path = os.path.join(tmp_path, "submodule")
    os.makedirs(submodule_path, exist_ok=True)

    init_path = os.path.join(tmp_path, "__init__.py")
    with open(init_path, 'w') as f:
        pass
    
    node_1_path = os.path.join(tmp_path, "node_1.py")
    with open(node_1_path, 'w') as f:
        f.write(node_1_code)

    init_submodule_path = os.path.join(submodule_path, "__init__.py")
    with open(init_submodule_path, 'w') as f:
        pass
    
    node_2_path = os.path.join(submodule_path, "node_2.py")
    with open(node_2_path, 'w') as f:
        f.write(node_2_code)



def test_load_nodes(tmp_path):
    node_1_code = '''from nodemodel import node

@node(x=2)
def b(a, y):
    return a + y

@node
def a(x):
    return x

def z(u):
    return u
'''

    node_2_code = '''from nodemodel import node

@node
def e(b):
    return b * 5

@node(y=3)
def c(b):
    return b
'''
    create_folder_structure(tmp_path,node_1_code,node_2_code)
    nodes = load_nodes(tmp_path)
    m = Model(nodes)
    assert m.compute({"x":1,"y":1}) == {'x': 1, 'y': 1, 'a': 1, 'b': 3, 'e': 15, 'c': 5}


def test_load_callable_nodes_from_globals(tmp_path):
    node_1_code = '''from nodemodel import node

class A():
    def __init__(self,v:str,coeff:float):
        self.name = f"a_{v}"
        self.y = f"y_{v}"
        self.inputs = {"y":self.y}
        self.coeff = coeff

    def __call__(self,x,y):
        return (x * self.coeff) + y

a_config = [{"v":"k","coeff":1},{"v":"l","coeff":2},{"v":"m","coeff":3}]

for config in a_config:
    globals()[A(**config).name] = node(A(**config))
'''


    node_2_code = '''from nodemodel import node

class B():
    def __init__(self,v:str,forced_value:float):
        self.name = f"b_{v}"
        self.a = f"a_{v}"
        self.inputs = {"a":self.a}
        self.forced_nodes = {"x":forced_value}
        
    def __call__(self,a):
        return a

b_config = [{"v":"k","forced_value":1},{"v":"l","forced_value":10},{"v":"m","forced_value":100}]

for config in b_config:
    globals()[B(**config).name] = node(B(**config))
'''

    create_folder_structure(tmp_path,node_1_code,node_2_code)
    nodes = load_nodes(tmp_path)
    m = Model(nodes)
    assert m.compute({"x":1000,"y_k":0.1,"y_l":0.2,"y_m":0.3}) == {'x': 1000, 'y_k': 0.1, 'y_l': 0.2, 'y_m': 0.3, 
                                                                   'a_k': 1000.1, 'a_l': 2000.2, 'a_m': 3000.3, 
                                                                   'b_k': 1.1, 'b_l': 20.2, 'b_m': 300.3}

def test_load_callable_nodes_from_dictionary(tmp_path):
    node_1_code = '''from nodemodel import node

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

a_b_nodes = {}
a_b_nodes['A'] = {}
a_b_nodes['B'] = {}

a_config = [{"v":"k","coeff":1},{"v":"l","coeff":2},{"v":"m","coeff":3}]
b_config = [{"v":"k","forced_value":1},{"v":"l","forced_value":10},{"v":"m","forced_value":100}]

for config in a_config:
    a_b_nodes['A'][A(**config).name] = node(A(**config))

for config in b_config:
    a_b_nodes['B'][B(**config).name] = node(B(**config))
'''


    node_2_code = ''''''

    create_folder_structure(tmp_path,node_1_code,node_2_code)
    nodes = load_nodes(tmp_path)
    m = Model(nodes)
    assert m.compute({"x":1000,"y_k":0.1,"y_l":0.2,"y_m":0.3}) == {'x': 1000, 'y_k': 0.1, 'y_l': 0.2, 'y_m': 0.3, 
                                                                   'a_k': 1000.1, 'a_l': 2000.2, 'a_m': 3000.3, 
                                                                   'b_k': 1.1, 'b_l': 20.2, 'b_m': 300.3}