"""
Configuration file for the Sphinx documentation builder.
"""

import os
import sys

sys.path.insert(0, os.path.abspath("../../"))

# -- Project information -----------------------------------------------------
project = "Mahjong score management tool"
copyright = "2026, togakushi"
author = "togakushi"

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
]

templates_path = ["templates"]
exclude_patterns = []

# -- Options for autodoc ----------------------------------------------------
autodoc_typehints = "description"
autodoc_class_signature = "separated"

# -- Napoleon settings ------------------------------------------------------
napoleon_google_docstring = True
napoleon_numpy_docstring = True

# -- Options for HTML output -------------------------------------------------
html_theme = "python_docs_theme"
