nodemodel
=========

.. image:: https://github.com/krzysztof-pankow/nodemodel/actions/workflows/quality.yml/badge.svg
   :target: https://github.com/krzysztof-pankow/nodemodel/actions?query=workflow%3Atest

.. image:: https://codecov.io/github/krzysztof-pankow/nodemodel/graph/badge.svg?token=00PQHNZH4W
   :target: https://codecov.io/github/krzysztof-pankow/nodemodel

.. image:: https://readthedocs.org/projects/nodemodel/badge/?version=latest
   :target: https://nodemodel.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. image:: https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue
   :target: https://pypi.python.org/pypi/nodemodel


Nodemodel is a small Python package for generating and computing a graph based on a dictionary of functions. It uses the function names and their argument names to define relationships within the graph.

- **Source:** https://github.com/krzysztof-pankow/nodemodel
- **Tutorial:** https://nodemodel.readthedocs.io/en/latest

Main Features
-------------
- **Simple Interface** – Use a single class, ``Model``, to generate a graph of functions, and its method ``compute`` to compute the graph on a dictionary.
- **Organizes Your Code** – Add a ``@node`` decorator to your functions and load them with the ``load_nodes`` function for easy management.
- **Supports Conditional Functions** – Easily specify that the computation of a function depends on modified inputs or the modified results of other functions.
- **Lightweight** – ``nodemodel`` only depends on the ``networkx`` package; everything else is pure Python.
- **Efficient** – Avoids copying data and executes all functions iteratively to maximize performance.

Example: Basic
--------------

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
   m = Model({"a": a, "b": b, "c": c, "d": d})

   # Compute values for the given inputs
   result = m.compute({"x": 1, "y": 2})
   print(result)  # Output: {'x': 1, 'y': 2, 'a': 2, 'b': 3, 'd': 20, 'c': 5}

   # Compute only a part of the model
   result = m.submodel("d").compute({"x": 1, "y": 2})
   print(result)  # Output: {'x': 1, 'y': 2, 'a': 2, 'd': 20}

Example: Conditional functions
------------------------------

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

Example: Node decorators
------------------------

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

Example: Callable objects
------------------------------------
Callable objects can be used in place of functions as nodes within the model:

.. code-block:: python

    class W:
        def __init__(self, k):
            # Define input mapping so `x` is taken from `x_k` in the input dictionary
            self.inputs = {"x": f"x_{k}"}

        def __call__(self, x):
            return x

    # Initialize the model with instances of `W` as nodes
    m = Model({"a": W(1), "b": W(2), "c": W(3)})

    # Compute with inputs mapped accordingly
    print(m.compute({"x_1": 6, "x_2": 7, "x_3": 8}))
    # Output: {'x_1': 6, 'x_2': 7, 'x_3': 8, 'a': 6, 'b': 7, 'c': 8}

In this example, instances of the class `W` act as callable nodes in the model. Each `W` instance has an `inputs` 
attribute that specifies a mapping for the argument `x`. For instance, the node `"a"` maps `x` to `x_1`, node `"b"` 
maps `x` to `x_2`, and node `"c"` maps `x` to `x_3`. During computation, `Model.compute` uses this mapping to link 
input values correctly, allowing each node to retrieve its input from the appropriate key in the input dictionary.

This approach enables flexibility, as users can pass callable objects with custom input mappings rather than 
requiring each node to have an exact name match with its inputs.

Example: Using nodemodel with Pandas
------------------------------------

Nodemodel can be useful for working with different data structures.
For example, with `pandas` DataFrames:

.. code-block:: python

   import pandas as pd
   df = pd.DataFrame({"x": [1, 2, 3],"y": [2, 3, 4]})

   df = df.to_dict(orient="series")
   result = pd.DataFrame(m.compute(df))
   print(result)

      x  y  a  b    c   d
   0  1  2  2  3  104  30
   1  2  3  3  4  105  40
   2  3  4  4  5  106  50

Installation
------------
You can install `nodemodel` using `pip`:

.. code-block:: bash

   pip install nodemodel
