"""
Configuration file for the Sphinx documentation builder.
"""

import os
import sys
import tomllib
from pathlib import Path
from typing import Any

sys.path.insert(0, os.path.abspath("../../"))
sys.path.append(str(Path("extensions").resolve()))

with open("../../pyproject.toml", mode="rb") as toml_file:
    toml_data: dict[str, Any] = tomllib.load(toml_file)
    project_data: dict[str, Any] = toml_data.get("project", {})

# -- Project information -----------------------------------------------------
project = "User's Manual"
author = "togakushi"
copyright = f"%Y, {author}"
version = project_data.get("version", "")
release = project_data.get("version", "")
primary_domain = "mahjong"

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.githubpages",
    "sphinx.ext.intersphinx",
    "sphinxcontrib.mermaid",
    "linuxdoc.rstFlatTable",
    "mahjong_domain",
]
templates_path = ["../customization/templates"]
rst_epilog = """
.. |:o:| unicode:: U+2B55
.. |:x:| unicode:: U+274C
.. |:/:| unicode:: U+2714
.. |:-:| unicode:: U+2504
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
html_search_language = "ja"
html_show_search_summary = True
html_show_sourcelink = True
html_static_path = ["../customization/static"]
html_css_files = ["user_doc.css"]
html_theme_options = {
    "root_icon": "ma-jan_pai.png",
    "root_url": "",
    "root_name": "",
    "globaltoc_collapse": True,
}
html_sidebars = {
    "**": [
        "localtoc.html",
        "globaltoc.html",
        "links.html",
    ],
}

# -- Options for intersphinx -------------------------------------------------
intersphinx_mapping = {
    "api": (
        "../../../api/build/html/",
        (str(Path(__file__).parent / "../api/build/html/objects.inv"), None),
    ),
}
