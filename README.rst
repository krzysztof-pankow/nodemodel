nodemodel
========

Nodemodel is a small Python package for generating and computing a graph based on a dictionary of functions. It uses the function names and their argument names to define relationships within the graph.

Main Features
--------------
- **Simple Interface** – Use a single class, ``Model``, to generate a graph of functions, and its method ``compute`` to compute the graph on a dictionary.
- **Organizes Your Code** – Add a ``@node`` decorator to your functions and load them with the ``load_nodes`` function for easy management.
- **Supports Conditional Functions** – Easily specify that the computation of a function depends on modified inputs or the results of other functions.
- **Lightweight** – ``nodemodel`` only depends on the ``networkx`` package; everything else is pure Python.
- **Efficient** – Avoids copying data and executes all functions iteratively to maximize performance.

Examples
--------------

Basic Example
^^^^^^^^^^

.. code-block:: python

    from nodemodel import Model
    
    # Define functions:
    def c(a, b):
        return a * b
    
    def a(x):
        return x + 1
    
    def b(a, y):
        return y + 2 * a
    
    # Initialize the model with the defined functions
    m = Model({"a": a, "b": b, "c": c})
    
    # Compute values for the given inputs
    result = m.compute({"x": 5, "y": 2})
    print(result)  # Output: {'x': 5, 'y': 2, 'a': 6, 'b': 14, 'c': 84}

Example With Conditional Function
^^^^^^^^^^

.. code-block:: python

    #c will be calculated with x forced to 100
    c.forced_nodes = {"x":100}
    
    # Reinitialize the model:
    m = Model({"a":a,"b":b,"c":c})
    
    #Compute the model on a dictionary:
    result = m.compute({"x": 5, "y": 2})
    print(result)  # Output: {'x': 5, 'y': 2, 'a': 6, 'b': 14, 'c': 20604}

Please notice that only "c" value changed after computing the model.

Example With Node Decorators
^^^^^^^^^^

Suppose we have the following file structure:

.. code-block:: text

    my_model/
    ├── __init__.py
    ├── c_code.py
    ├── a_and_b/
    │   ├── __init__.py
    │   └── a_and_b_code.py

We will place the example functions in these files:

**c_code.py**

.. code-block:: python

    from nodemodel import node

    @node(x=100)
    def c(a, b):
        return a * b

**a_and_b_code.py**

.. code-block:: python

    from nodemodel import node

    @node
    def a(x):
        return x + 1

    @node
    def b(a, y):
        return y + 2 * a

Now we can load and execute these functions using the `nodemodel` package:

.. code-block:: python

    from nodemodel import Model, load_nodes

    # Import all functions with a @node decorator from the "my_model" directory
    nodes = load_nodes("my_model")

    # Initialize the model with the loaded functions
    m = Model(nodes)

Installation
--------------
You can install `nodemodel` using `pip`:

.. code-block:: bash

    pip install nodemodel
