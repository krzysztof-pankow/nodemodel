from nodemodel.utils import load_nodes
from nodemodel.model import Model
import os

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

def create_folder_structure(tmp_path):
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
    create_folder_structure(tmp_path)
    nodes = load_nodes(tmp_path)
    m = Model(nodes)
    assert m.compute({"x":1,"y":1}) == {'x': 1, 'y': 1, 'a': 1, 'b': 3, 'e': 15, 'c': 5}
