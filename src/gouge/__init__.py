"""
Logging formatters for the Python :mod:`logging` module.

The package provides colourful console output
(:class:`gouge.colourcli.Simple`), parseable key/value output
(:mod:`gouge.parseable`), message pre-formatters
(:mod:`gouge.preformatters`) and helper filters (:mod:`gouge.filters`).
"""

from importlib import metadata

try:
    __version__ = metadata.version("gouge")
except metadata.PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0+unknown"

__all__ = ["__version__"]
