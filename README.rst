nodemodel
========

.. image:: https://github.com/krzysztof-pankow/nodemodel/actions/workflows/quality.yml/badge.svg
    :target: https://github.com/krzysztof-pankow/nodemodel/actions?query=workflow%3Atest
.. image:: https://codecov.io/github/krzysztof-pankow/nodemodel/graph/badge.svg?token=00PQHNZH4W
    :target: https://codecov.io/github/krzysztof-pankow/nodemodel
.. image:: https://readthedocs.org/projects/nodemodel/badge/?version=latest
    :target: https://nodemodel.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status


Nodemodel is a small Python package for generating and computing a graph based on a dictionary of functions. It uses the function names and their argument names to define relationships within the graph.

- **Source:** https://github.com/krzysztof-pankow/nodemodel
- **Tutorial:** https://nodemodel.readthedocs.io/en/latest

Main Features
--------------
- **Simple Interface** – Use a single class, ``Model``, to generate a graph of functions, and its method ``compute`` to compute the graph on a dictionary.
- **Organizes Your Code** – Add a ``@node`` decorator to your functions and load them with the ``load_nodes`` function for easy management.
- **Supports Conditional Functions** – Easily specify that the computation of a function depends on modified inputs or the modified results of other functions.
- **Lightweight** – ``nodemodel`` only depends on the ``networkx`` package; everything else is pure Python.
- **Efficient** – Avoids copying data and executes all functions iteratively to maximize performance.

Examples
--------------

Basic Example
^^^^^^^^^^

.. code-block:: python

    from nodemodel import Model
    
    # Define functions:
    def d(a):
        return a * 10
    
    def c(a, b):
        return a + b

    def b(y):
        return y + 1
    
    def a(x):
        return x + 1
    
    # Initialize the model with the defined functions
    m = Model({"a": a, "b": b, "c": c,"d": d})
    
    # Compute values for the given inputs
    result = m.compute({"x": 1, "y": 2})
    print(result)  # Output: {'x': 1, 'y': 2, 'a': 2, 'b': 3, 'd': 20, 'c': 5}
    
    # Compute only a part of the model
    result = m.submodel("d").compute({"x": 1, "y": 2})
    print(result)  # Output: {'x': 1, 'y': 2, 'a': 2, 'd': 20}

Example With Conditional Functions
^^^^^^^^^^

.. code-block:: python

    #"c" will be calculated with "x" forced to 100
    c.forced_nodes = {"x":100}
    
    #"d" will be calculated with "a" forced to "b"
    d.forced_nodes = {"a":("node","b")}
    
    # Reinitialize the model:
    m = Model({"a": a, "b": b, "c": c,"d": d})
    
    #Compute the model on a dictionary:
    result = m.compute({"x": 1, "y": 2})
    print(result)  # Output: {'x': 1, 'y': 2, 'a': 2, 'b': 3, 'c': 104, 'd': 30}

Please notice that only "c" and "d" values changed after computing the model.

Example With Node Decorators
^^^^^^^^^^

Suppose we have the following file structure:

.. code-block:: text

    my_model/
    ├── __init__.py
    ├── c_and_d_code.py
    ├── a_and_b/
    │   ├── __init__.py
    │   └── a_and_b_code.py

We will place the example functions in these files:

**c_and_d_code.py**

.. code-block:: python

    from nodemodel import node

    @node(x=100)
    def c(a, b):
        return a + b

    @node(a=("node","b"))
    def d(a):
        return a * 10

**a_and_b_code.py**

.. code-block:: python

    from nodemodel import node

    @node
    def a(x):
        return x + 1

    @node
    def b(y):
        return y + 1

Now we can load and execute these functions using the `nodemodel` package:

.. code-block:: python

    from nodemodel import Model, load_nodes

    # Import all functions with a @node decorator from the "my_model" directory
    nodes = load_nodes("my_model")

    # Initialize the model with the loaded functions
    m = Model(nodes)

    #Compute the model on a dictionary:
    result = m.compute({"x": 1, "y": 2})
    print(result)  # Output: {'x': 1, 'y': 2, 'a': 2, 'b': 3, 'c': 104, 'd': 30}

Installation
--------------
You can install `nodemodel` using `pip`:

.. code-block:: bash

    pip install nodemodel
