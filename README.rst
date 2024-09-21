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

Installation
--------------
You can install `nodemodel` using `pip`:

.. code-block:: bash

    pip install nodemodel
