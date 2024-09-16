import os
import importlib

def node(f = None,tag = None,**forced_nodes):
    def decorator(g):
        g.node_tag = tag
        if len(forced_nodes) > 0:
            g.forced_nodes = forced_nodes
        return g
    
    if callable(f):
        f.node_tag = tag
        if len(forced_nodes) > 0:
            f.forced_nodes = forced_nodes
        return f
    else:
        return decorator

def dynamic_import(module_name, module_path):
    module_spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module

def dynamic_import_from_dir(module_dir):
    imported_dict = {}
    for root, dirs, files in os.walk(module_dir):
        for f in files:
            if f.endswith(".py"):
                module_path = os.path.join(root,f)
                module_name = f.split(".")[0]
                imported_module = dynamic_import(module_name, module_path)
                imported_dict.update(imported_module.__dict__)
    return imported_dict

def load_nodes(module_dir):
    imported_dict = dynamic_import_from_dir(module_dir)
    nodes = {k:v for k,v in imported_dict.items() if hasattr(v,"node_tag")}
    return nodes

