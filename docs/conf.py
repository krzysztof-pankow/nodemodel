# docs/conf.py

import os
import sys
import tomli
sys.path.insert(0, os.path.abspath('../'))  # This ensures Sphinx can find your nodemodel module

# Read version from pyproject.toml
with open("../pyproject.toml", "rb") as f:
    pyproject_data = tomli.load(f)  # For Python 3.11+, use tomllib instead of tomli
    version = pyproject_data["project"]["version"]  # Adjust this path depending on your pyproject.toml structure

# Project information
project = 'Nodemodel Documentation'
author = 'Krzysztof Pankow'
release = version

# General configuration
extensions = [
    'sphinx.ext.autodoc',       # For generating documentation from docstrings
    'sphinx.ext.napoleon',       # Supports Google and NumPy style docstrings
    'sphinx_autodoc_typehints',  # To automatically document types
    'sphinx_copybutton',  # To enable the copy button
]

# Paths
templates_path = ['_templates']
exclude_patterns = []

# HTML output options
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Include README.rst as the main page
master_doc = 'index'
