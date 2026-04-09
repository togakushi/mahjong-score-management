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
project = "User's Manual"
author = "togakushi"
copyright = f"%Y, {author}"
version = project_data.get("version", "")
release = project_data.get("version", "")

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.githubpages",
    "sphinxcontrib.mermaid",
]
templates_path = ["../templates"]
rst_epilog = """
.. |:o:| unicode:: U+2B55
.. |:x:| unicode:: U+274C
.. |:/:| unicode:: U+2714
"""
manpages_url = "https://github.com/togakushi/mahjong-score-management/tree/main/files/{path}"
default_role = "any"

# -- Options for HTML output -------------------------------------------------
html_theme = "python_docs_theme"
html_title = f"{project}"
html_last_updated_fmt = "%Y-%m-%d"
html_split_index = False
html_show_sphinx = False
html_show_copyright = False
html_static_path = ["source/_static"]
html_css_files = ["custom.css"]
html_theme_options = {
    "root_icon": "ma-jan_pai.png",
    "root_url": "",
    "root_name": "",
}
html_sidebars = {
    "**": [
        "localtoc.html",
        "relations.html",
        "sourcelink.html",
        "links.html",
    ],
}
