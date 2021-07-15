# Configuration file for the Sphinx documentation builder.

project = "qiskit-rigetti-provider"
copyright = "2021, Rigetti Computing"
author = "Andrew Meyer"

# The full version, including alpha/beta/rc tags
from qiskit_rigetti_provider import __version__

release = __version__


# -- General configuration ---------------------------------------------------

extensions = ["autoapi.extension", "sphinx.ext.napoleon", "myst_parser"]

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

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
html_theme = "furo"
# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
