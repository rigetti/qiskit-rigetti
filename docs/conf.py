# Configuration file for the Sphinx documentation builder.

project = "qiskit-rigetti-provider"
copyright = "2021, Rigetti Computing"
author = "Rigetti Computing"

# The full version, including alpha/beta/rc tags
from qiskit_rigetti_provider import __version__

release = __version__


# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "autoapi.extension",
    "sphinx.ext.napoleon",
    "myst_parser",
]

source_suffix = {
    ".rst": "restructuredtext",
    ".txt": "markdown",
    ".md": "markdown",
}

# Document Python Code
autoapi_type = "python"
autoapi_python_class_content = "both"
autoapi_dirs = ["../qiskit_rigetti_provider"]
autoapi_options = [
    "members",
    "undoc-members",
    "show-inheritance",
    "show-module-summary",
    "special-members",
    "imported-members",
]
autoapi_generate_api_docs = False

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
html_theme = "furo"
html_theme_options = {
    "light_css_variables": {
        "color-brand-primary": "#00b5ad",
        "color-problematic": "#66d3ce",
        "color-brand-content": "#3D47D9 ",
    },
    "dark_css_variables": {
        "color-brand-content": "#8b91e8",
    },
}
