"""
Configuration file for the Sphinx documentation builder.
"""

import os
import sys
import tomllib
from typing import Any

sys.path.insert(0, os.path.abspath("../../"))

with open("../../pyproject.toml", mode="rb") as toml_file:
    toml_data: dict[str, Any] = tomllib.load(toml_file)
    project_data: dict[str, Any] = toml_data.get("project", {})

# -- Project information -----------------------------------------------------
project = "Developer"
author = "togakushi"
copyright = f"%Y, {author}"
version = project_data.get("version", "")
release = project_data.get("version", "")

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.githubpages",
]

templates_path = ["templates"]

# -- Options for autodoc -----------------------------------------------------
autodoc_typehints = "description"
autodoc_class_signature = "separated"

# -- Napoleon settings -------------------------------------------------------
napoleon_google_docstring = True
napoleon_numpy_docstring = True

# -- Options for HTML output -------------------------------------------------
html_theme = "python_docs_theme"
html_title = f"{project} Documentation"
html_last_updated_fmt = "%Y-%m-%d"
html_split_index = False
html_show_sphinx = False
html_show_copyright = False
