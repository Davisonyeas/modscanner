"""Sphinx configuration for modscanner."""

from importlib.metadata import version as package_version


project = "ModScanner"
author = "Davis Onyeoguzoro"

release = package_version("modscanner")
version = release

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
]

templates_path = ["_templates"]

exclude_patterns: list[str] = []

html_theme = "sphinx_rtd_theme"

html_title = f"ModScanner {release}"

html_static_path = ["_static"]

autodoc_typehints = "description"
autodoc_member_order = "bysource"

myst_enable_extensions = [
    "colon_fence",
    "deflist",
]

intersphinx_mapping = {
    "python": (
        "https://docs.python.org/3",
        None,
    ),
}