from warnings import warn

from pkg_resources import resource_string

__version__ = resource_string("gouge", "version.txt").decode("ascii").strip()
warn(
    "gouge 1.x is deprecated and no longer maintained. Please upgrade to 2.x",
    DeprecationWarning,
    stacklevel=2,
)
