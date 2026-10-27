"""
Logging formatters for the Python :mod:`logging` module.

The package provides colourful console output
(:class:`gouge.colourcli.Simple`), machine-readable output
(:mod:`gouge.parseable`), message pre-formatters
(:mod:`gouge.preformatters`), uvicorn support (:mod:`gouge.uvicorn`) and
helper filters (:mod:`gouge.filters`).
"""

from importlib import metadata

#: The installed version of gouge, for example ``"2.3.0"``.
__version__: str
try:
    __version__ = metadata.version("gouge")
except metadata.PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0+unknown"

__all__ = ["__version__"]
