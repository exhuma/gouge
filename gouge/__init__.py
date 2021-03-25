from pkg_resources import resource_string

__version__ = resource_string("gouge", "version.txt").decode("ascii").strip()
