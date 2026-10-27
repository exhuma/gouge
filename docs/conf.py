import tomllib
from pathlib import Path

with open(Path(__file__).parent.parent / "pyproject.toml", "rb") as f:
    _meta = tomllib.load(f)

project = "gouge"
copyright = "2015, Michel Albert"
author = "Michel Albert"
release = _meta["project"]["version"]
version = ".".join(release.split(".")[:2])

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.intersphinx",
    "sphinx_autodoc_typehints",
    "michel_albert_sphinx",
]

autosectionlabel_prefix_document = True
autodoc_member_order = "bysource"
intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_title = "gouge"
html_baseurl = "https://exhuma.github.io/gouge/"
html_theme_options = {
    "repo_url": "https://github.com/exhuma/gouge",
    "repo_name": "exhuma/gouge",
    "edit_uri": "blob/master/docs",
    "features": [
        "content.code.copy",
        "navigation.top",
        "toc.follow",
    ],
}
